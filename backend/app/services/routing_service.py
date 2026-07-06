from app.schemas.ticket import Routing


def determine_routing(sensitivity_level: str) -> Routing:
    """Choose provider, model, and routing configuration based on sensitivity level."""
    if sensitivity_level == "high":
        return Routing(
            selected_provider="ollama",
            selected_model="llama3",
            route_type="compliance_enforced",
            reason="High-sensitivity ticket containing compliance risks routed to local hardware.",
            escalation_used=True
        )
    elif sensitivity_level == "medium":
        return Routing(
            selected_provider="ollama",
            selected_model="llama3",
            route_type="compliance_enforced",
            reason="Medium-sensitivity ticket containing PII/finance details routed to local hardware.",
            escalation_used=True
        )
    else:
        return Routing(
            selected_provider="groq",
            selected_model="mixtral-8x7b",
            route_type="cost_optimized",
            reason="Low-sensitivity ticket routed to cost-optimized cloud model.",
            escalation_used=False
        )
