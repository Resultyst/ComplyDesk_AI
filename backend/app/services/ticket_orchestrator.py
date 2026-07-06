from uuid import uuid4
import logging

from app.repositories import customer_repo, audit_repo
from app.services import (
    sensitivity_service,
    response_service,
    memory_extraction_service,
    memory_normalization_service,
    cost_accounting_service,
    prompt_builder,
)
from app.services.memory_provider import get_memory_provider
from app.providers.llm.groq_provider import GroqLLMProvider
from app.providers.llm.ollama_provider import OllamaLLMProvider
from app.services.cascadeflow_router_adapter import CascadeflowRouterAdapter

from app.schemas.ticket import (
    TicketProcessRequest,
    TicketProcessResponse,
    Memory,
    Metrics,
    AuditEntry,
)
from app.utils import utc_now

logger = logging.getLogger(__name__)

def process_ticket(request: TicketProcessRequest) -> TicketProcessResponse:
    """Orchestrates the complete ticket processing pipeline using hardened integrations."""
    ticket_id = f"TKT-{uuid4().hex[:8].upper()}"
    now = utc_now()

    # 1. Load customer
    customer = customer_repo.get_customer_by_id(request.customer_id)
    if not customer:
        raise ValueError(f"Customer {request.customer_id} not found")

    customer_name = customer["name"]
    preferred_channel = customer["preferred_channel"]
    account_type = customer["account_type"]
    plan_tier = customer["plan_tier"]

    # 2. Recall memory via memory provider (Hindsight Cloud with local fallback)
    memory_provider = get_memory_provider()
    memory_items = memory_provider.get_memory_items(request.customer_id)
    # Normalize, translate, and deduplicate on retrieval
    memory_items = memory_normalization_service.filter_and_rank_memories(request.customer_id, memory_items)
    memory_source = getattr(memory_provider, "last_used_source", "local_fallback")

    # 3. Classify sensitivity
    sensitivity = sensitivity_service.classify_sensitivity(request.ticket_text)

    # 4. Choose routing via Cascadeflow Router Adapter (health and budget-aware)
    router = CascadeflowRouterAdapter()
    routing = router.determine_routing(sensitivity.level)

    # 5. Build prompt
    prompt = prompt_builder.build_support_prompt(
        customer_name=customer_name,
        preferred_channel=preferred_channel,
        account_type=account_type,
        plan_tier=plan_tier,
        memory_items=memory_items,
        sensitivity_level=sensitivity.level,
        risk_tags=sensitivity.risk_tags,
        ticket_text=request.ticket_text
    )

    # Instantiate LLM providers
    groq_provider = GroqLLMProvider()
    ollama_provider = OllamaLLMProvider()

    # 6. Generate support response with LLM Provider and Fallback Hierarchy
    llm_result = None
    fallback_occurred = False

    if routing.selected_provider == "groq":
        try:
            logger.info("Attempting cloud inference via Groq...")
            llm_result = groq_provider.generate_response(prompt)
            if llm_result.get("is_fallback"):
                fallback_occurred = True
        except Exception as e:
            logger.warning(f"Groq provider failed: {e}. Switching to Ollama local compliance model fallback...")
            fallback_occurred = True
            try:
                llm_result = ollama_provider.generate_response(prompt)
                routing.selected_provider = "ollama"
                routing.selected_model = llm_result["model_used"]
                routing.route_type = "fallback"
                routing.reason = f"Groq cloud model failed; routed to local Ollama compliance fallback. [{routing.reason.split('[')[-1]}"
            except Exception as e2:
                logger.error(f"Ollama fallback also failed: {e2}. Falling back to local rules engine.")
                # Degraded local fallback
                response_text = response_service.generate_response(
                    customer_name=customer_name,
                    preferred_channel=preferred_channel,
                    memory_items=memory_items,
                    sensitivity_level=sensitivity.level,
                    risk_tags=sensitivity.risk_tags,
                    ticket_text=request.ticket_text,
                )
                llm_result = {
                    "response_text": response_text,
                    "model_used": "local-rules-engine",
                    "provider": "degraded_local",
                    "latency_ms": 120,
                    "cost_usd": 0.0
                }
                routing.selected_provider = "degraded_local"
                routing.selected_model = "local-rules-engine"
                routing.route_type = "degraded_local_response"
                routing.reason = f"All external LLMs failed; generated response via rules engine. [{routing.reason.split('[')[-1]}"

    elif routing.selected_provider == "ollama":
        try:
            logger.info("Attempting local compliance inference via Ollama...")
            llm_result = ollama_provider.generate_response(prompt)
            if llm_result.get("is_fallback"):
                fallback_occurred = True
        except Exception as e:
            logger.warning(f"Ollama provider failed: {e}. Falling back to local rules engine...")
            fallback_occurred = True
            response_text = response_service.generate_response(
                customer_name=customer_name,
                preferred_channel=preferred_channel,
                memory_items=memory_items,
                sensitivity_level=sensitivity.level,
                risk_tags=sensitivity.risk_tags,
                ticket_text=request.ticket_text,
            )
            llm_result = {
                "response_text": response_text,
                "model_used": "local-rules-engine",
                "provider": "degraded_local",
                "latency_ms": 120,
                "cost_usd": 0.0
            }
            routing.selected_provider = "degraded_local"
            routing.selected_model = "local-rules-engine"
            routing.route_type = "degraded_local_response"
            routing.reason = f"Local Ollama failed; generated response via rules engine. [{routing.reason.split('[')[-1]}"

    # Fallback response for degraded_local default setup
    else:
        response_text = response_service.generate_response(
            customer_name=customer_name,
            preferred_channel=preferred_channel,
            memory_items=memory_items,
            sensitivity_level=sensitivity.level,
            risk_tags=sensitivity.risk_tags,
            ticket_text=request.ticket_text,
        )
        llm_result = {
            "response_text": response_text,
            "model_used": "local-rules-engine",
            "provider": "degraded_local",
            "latency_ms": 120,
            "cost_usd": 0.0
        }

    response_text = llm_result["response_text"]
    latency_ms = llm_result["latency_ms"]
    cost_usd = llm_result["cost_usd"]

    # 7. Extract new memory facts
    new_facts = memory_extraction_service.extract_new_memories(
        ticket_text=request.ticket_text,
        sensitivity_level=sensitivity.level,
    )

    # 8. Normalize and deduplicate before Hindsight write
    filtered_facts = memory_normalization_service.deduplicate_memories(
        existing_items=memory_items,
        new_facts=new_facts
    )

    # 9. Store unique new memory facts via provider
    for fact in filtered_facts:
        memory_provider.append_memory_item(
            customer_id=request.customer_id,
            key=fact.key,
            value=fact.value,
            source=fact.source,
        )

    # Re-fetch memories to include the newly appended ones in the response
    updated_memory_items = memory_provider.get_memory_items(request.customer_id)
    updated_memory_items = memory_normalization_service.filter_and_rank_memories(request.customer_id, updated_memory_items)

    # 10. Cost accounting calculations
    cost_data = cost_accounting_service.calculate_ticket_cost(
        sensitivity_level=sensitivity.level,
        provider=routing.selected_provider,
        actual_cost_usd=cost_usd
    )
    actual_cost = cost_data["actual_cost_usd"]
    cost_saved = cost_data["cost_saved_usd"]
    baseline_cost = cost_data["baseline_cost_usd"]

    metrics = Metrics(
        latency_ms=latency_ms,
        estimated_cost_usd=actual_cost,
    )

    # 11. Memory influence and delta analysis
    key_facts_used = []
    influence_summary = "No prior memory context influenced this response."
    
    ticket_text_lower = request.ticket_text.lower()
    has_prior_duplicate_debit = any("duplicate debit" in item.value.lower() or "charged twice" in item.value.lower() for item in memory_items)
    has_prior_kyc_delay = any("kyc" in item.value.lower() or "verification" in item.value.lower() for item in memory_items)
    has_prior_suspicious_debit = any("suspicious debit" in item.value.lower() or "monitored" in item.value.lower() for item in memory_items)
    prefers_email_disputes = any("email" in item.value.lower() and ("dispute" in item.value.lower() or "compliance" in item.value.lower()) for item in memory_items)
    
    is_refund = "refund" in ticket_text_lower
    is_kyc = "kyc" in ticket_text_lower or "verification" in ticket_text_lower or "document" in ticket_text_lower
    is_dispute = "charge" in ticket_text_lower or "debit" in ticket_text_lower or "unauthorized" in ticket_text_lower
    
    if is_dispute and has_prior_duplicate_debit:
        key_facts_used.append("prior_duplicate_debit")
        influence_summary = "Referenced customer preference and prior duplicate debit dispute history."
    elif is_dispute and has_prior_suspicious_debit:
        key_facts_used.append("prior_suspicious_debit")
        influence_summary = "Referenced account flag history and prior suspicious debit attempts."
    elif is_kyc and has_prior_kyc_delay:
        key_facts_used.append("prior_kyc_delay")
        influence_summary = "Referenced previous KYC verification delays and document resubmissions."
    elif prefers_email_disputes and ("email" in ticket_text_lower or "dispute" in ticket_text_lower):
        key_facts_used.append("email_disputes_preference")
        influence_summary = "Referenced customer preference for email updates for billing disputes."

    # 12. Create audit record
    audit_id = f"AUD-{uuid4().hex[:8].upper()}"
    decision_summary = (
        f"Sensitivity: {sensitivity.level} | Model: {routing.selected_provider}/{routing.selected_model} | "
        f"Route: {routing.route_type} | Latency: {latency_ms}ms"
    )
    audit_entry = AuditEntry(
        audit_id=audit_id,
        timestamp=now,
        decision_summary=decision_summary,
    )

    # Enrich routing reason with memory details and cost accounting
    final_routing_reason = (
        f"{routing.reason} | Memory: {memory_source} (recalled={len(memory_items)}) | "
        f"Cost saved: ${cost_saved:.5f} (baseline: ${baseline_cost:.5f}, actual: ${actual_cost:.5f})"
    )

    # Write audit record to store
    audit_repo.add_audit_record({
        "audit_id": audit_id,
        "timestamp": now,
        "ticket_id": ticket_id,
        "customer_id": request.customer_id,
        "sensitivity": sensitivity.level,
        "model_selected": f"{routing.selected_provider}/{routing.selected_model}",
        "routing_reason": final_routing_reason,
        "memory_used": len(updated_memory_items) > 0,
        "latency_ms": latency_ms,
        "estimated_cost_usd": actual_cost,
    })

    if memory_source == "hindsight":
        memory_summary = f"Retrieved {len(updated_memory_items)} memory items from customer history via Hindsight Cloud."
    else:
        memory_summary = f"Retrieved {len(updated_memory_items)} memory items from customer history via local memory fallback."

    memory_context = Memory(
        used=len(updated_memory_items) > 0,
        items=updated_memory_items,
        summary=memory_summary,
        source=memory_source,
        items_count=len(updated_memory_items),
        key_facts_used=key_facts_used,
        influence_summary=influence_summary
    )

    return TicketProcessResponse(
        ticket_id=ticket_id,
        customer_id=request.customer_id,
        response_text=response_text,
        memory=memory_context,
        sensitivity=sensitivity,
        routing=routing,
        metrics=metrics,
        audit=audit_entry,
    )
