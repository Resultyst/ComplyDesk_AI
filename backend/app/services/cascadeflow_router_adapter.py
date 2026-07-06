from app.schemas.ticket import Routing
from app.core import config
from app.services import provider_health_service

class CascadeflowRouterAdapter:
    """Orchestrates model routing decisions based on compliance, cost, and sensitivity."""

    def __init__(self) -> None:
        self.groq_model = config.GROQ_MODEL_LOW_SENSITIVITY
        self.ollama_model = config.OLLAMA_MODEL_PRIMARY

    def determine_routing(self, sensitivity_level: str) -> Routing:
        """Return a Cascadeflow-compatible routing decision based on sensitivity and health."""
        # Fetch health status snapshot
        health = provider_health_service.get_health_status()
        
        compliance_priority = sensitivity_level in ("high", "medium")
        budget_priority = not compliance_priority
        provider_unavailable = False
        fallback_triggered = False

        if compliance_priority:
            # Sensitive ticket -> enforce local Ollama routing
            if health["ollama"] == "healthy":
                reason = f"{sensitivity_level.capitalize()}-sensitivity ticket containing PII/compliance risks routed to local Ollama hardware."
                selected_provider = "ollama"
                selected_model = self.ollama_model
                route_type = "compliance_enforced"
            else:
                reason = f"Ollama local hardware is offline/degraded. Falling back to local rules engine for {sensitivity_level}-sensitivity ticket."
                selected_provider = "degraded_local"
                selected_model = "local-rules-engine"
                route_type = "degraded_local_response"
                provider_unavailable = True
                fallback_triggered = True
        else:
            # Low sensitivity -> cost-optimized cloud model (Groq)
            if health["groq"] == "healthy":
                reason = "Low-sensitivity ticket routed to cost-optimized Groq cloud model."
                selected_provider = "groq"
                selected_model = self.groq_model
                route_type = "cost_optimized"
            elif health["ollama"] == "healthy":
                reason = "Groq cloud provider is offline. Routed low-sensitivity ticket to local Ollama fallback."
                selected_provider = "ollama"
                selected_model = self.ollama_model
                route_type = "fallback"
                provider_unavailable = True
                fallback_triggered = True
            else:
                reason = "All external LLM providers offline. Routed low-sensitivity ticket to local rules engine."
                selected_provider = "degraded_local"
                selected_model = "local-rules-engine"
                route_type = "degraded_local_response"
                provider_unavailable = True
                fallback_triggered = True

        # Append structured metadata to the reason field for demo visibility
        metadata_str = (
            f" [Compliance: {compliance_priority}] [Budget: {budget_priority}] "
            f"[Health: Groq={health['groq']}, Ollama={health['ollama']}, Hindsight={health['hindsight']}]"
        )
        final_reason = reason + metadata_str

        return Routing(
            selected_provider=selected_provider,
            selected_model=selected_model,
            route_type=route_type,
            reason=final_reason,
            escalation_used=compliance_priority
        )
