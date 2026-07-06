from uuid import uuid4

from app.repositories import audit_repo
from app.schemas.customer import MemoryItem
from app.schemas.ticket import (
    AuditEntry,
    Memory,
    Metrics,
    Routing,
    Sensitivity,
    TicketProcessRequest,
    TicketProcessResponse,
)
from app.utils import utc_now


def _classify_sensitivity(text: str) -> tuple[str, list[str], str]:
    """Classify ticket sensitivity based on keyword analysis.

    Returns (level, risk_tags, reasoning).
    """
    text_lower = text.lower()

    # High sensitivity keywords
    high_keywords = ["fraud", "unauthorized", "stolen", "suspicious", "compromised"]
    for kw in high_keywords:
        if kw in text_lower:
            return (
                "high",
                ["pii_exposure", "financial_fraud", "regulatory_risk"],
                f"Ticket contains high-risk keyword '{kw}'. "
                "Classified as high sensitivity for compliance routing.",
            )

    # Medium sensitivity keywords
    medium_keywords = ["charged twice", "refund", "dispute", "duplicate charge", "overcharged"]
    for kw in medium_keywords:
        if kw in text_lower:
            return (
                "medium",
                ["pii_present", "financial_dispute"],
                f"Ticket contains financial dispute keyword '{kw}'. "
                "Classified as medium sensitivity — PII likely present.",
            )

    # Default to low
    return (
        "low",
        ["general_inquiry"],
        "No high-risk indicators detected. "
        "Classified as low sensitivity for cost-optimized routing.",
    )


def _generate_response(sensitivity_level: str, ticket_text: str) -> str:
    """Generate a mocked AI response based on sensitivity level."""
    responses = {
        "high": (
            "Thank you for reporting this security concern. I've immediately flagged "
            "this for our fraud investigation team. Your account has been placed under "
            "enhanced monitoring. A dedicated compliance specialist will contact you "
            "within 2 hours via your preferred channel. In the meantime, please do not "
            "share any account credentials. Reference number has been generated for tracking."
        ),
        "medium": (
            "I understand your concern about this billing discrepancy. I've reviewed "
            "your recent transactions and can confirm the duplicate charge. I'm initiating "
            "a refund process which typically completes within 3-5 business days. You'll "
            "receive a confirmation email with the refund details. Is there anything else "
            "I can help you with?"
        ),
        "low": (
            "Thank you for reaching out! I'd be happy to help you with your request. "
            "I've looked into this and have the information you need. Everything appears "
            "to be in good order. Please let me know if you have any follow-up questions "
            "or if there's anything else I can assist with."
        ),
    }
    return responses.get(sensitivity_level, responses["low"])


def _determine_routing(sensitivity_level: str) -> tuple[str, str, str, str]:
    """Determine model routing based on sensitivity.

    Returns (provider, model, route_type, reason).
    """
    if sensitivity_level == "high":
        return (
            "Ollama",
            "llama3",
            "local",
            "High-sensitivity ticket routed to approved local model for compliance",
        )
    elif sensitivity_level == "medium":
        return (
            "Ollama",
            "llama3",
            "local",
            "Medium-sensitivity ticket with PII routed to local model",
        )
    else:
        return (
            "Groq",
            "mixtral-8x7b",
            "cloud",
            "Low-sensitivity ticket routed to cost-optimized cloud model",
        )


def _get_metrics(sensitivity_level: str) -> tuple[int, float]:
    """Return mocked performance metrics. Returns (latency_ms, cost_usd)."""
    metrics_map = {
        "high": (850, 0.0),
        "medium": (620, 0.0),
        "low": (340, 0.003),
    }
    return metrics_map.get(sensitivity_level, (340, 0.003))


def process_ticket(request: TicketProcessRequest) -> TicketProcessResponse:
    """Process a support ticket through the mocked AI pipeline.

    Steps:
    1. Classify sensitivity
    2. Determine routing
    3. Generate response (mocked)
    4. Build memory context
    5. Log audit entry
    """
    ticket_id = f"TKT-{uuid4().hex[:8].upper()}"
    now = utc_now()

    # Step 1: Classify
    level, risk_tags, reasoning = _classify_sensitivity(request.ticket_text)

    # Step 2: Route
    provider, model, route_type, route_reason = _determine_routing(level)

    # Step 3: Generate response
    response_text = _generate_response(level, request.ticket_text)

    # Step 4: Build memory context (mocked)
    memory_items = [
        MemoryItem(
            key="preferred_contact",
            value="email",
            source="account_settings",
            timestamp="2026-06-15T10:00:00Z",
        ),
        MemoryItem(
            key="previous_issue_type",
            value="billing_dispute",
            source="ticket_history",
            timestamp="2026-06-20T14:30:00Z",
        ),
        MemoryItem(
            key="customer_tier",
            value="enterprise",
            source="crm",
            timestamp="2026-07-01T09:00:00Z",
        ),
    ]

    memory = Memory(
        used=True,
        items=memory_items,
        summary="Retrieved 3 memory items from customer history via Hindsight.",
    )

    sensitivity = Sensitivity(
        level=level,
        risk_tags=risk_tags,
        reasoning=reasoning,
    )

    routing = Routing(
        selected_provider=provider,
        selected_model=model,
        route_type=route_type,
        reason=route_reason,
    )

    latency_ms, cost_usd = _get_metrics(level)
    metrics = Metrics(latency_ms=latency_ms, estimated_cost_usd=cost_usd)

    # Step 5: Audit entry
    audit_id = f"AUD-{uuid4().hex[:8].upper()}"
    audit_entry = AuditEntry(
        audit_id=audit_id,
        timestamp=now,
        decision_summary=(
            f"Sensitivity: {level} | Model: {provider}/{model} | "
            f"Route: {route_type} | Latency: {latency_ms}ms"
        ),
    )

    # Persist audit record
    audit_repo.add_audit_record({
        "audit_id": audit_id,
        "timestamp": now,
        "ticket_id": ticket_id,
        "customer_id": request.customer_id,
        "sensitivity": level,
        "model_selected": f"{provider}/{model}",
        "routing_reason": route_reason,
        "memory_used": True,
        "latency_ms": latency_ms,
        "estimated_cost_usd": cost_usd,
    })

    return TicketProcessResponse(
        ticket_id=ticket_id,
        customer_id=request.customer_id,
        response_text=response_text,
        memory=memory,
        sensitivity=sensitivity,
        routing=routing,
        metrics=metrics,
        audit=audit_entry,
    )
