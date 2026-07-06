from pydantic import BaseModel

from app.schemas.customer import MemoryItem


class TicketProcessRequest(BaseModel):
    """Incoming ticket processing request."""
    customer_id: str
    ticket_text: str
    use_demo_mode: bool = True


class Memory(BaseModel):
    """Memory context used when generating the response."""
    used: bool
    items: list[MemoryItem]
    summary: str
    source: str = "local_fallback"
    items_count: int = 0
    key_facts_used: list[str] = []
    influence_summary: str = "No prior memory context influenced this response."


class Sensitivity(BaseModel):
    """Sensitivity classification result."""
    level: str  # low | medium | high
    risk_tags: list[str]
    reasoning: str


class Routing(BaseModel):
    """Model routing decision."""
    selected_provider: str
    selected_model: str
    route_type: str  # compliance_enforced | cost_optimized
    reason: str
    escalation_used: bool = False


class Metrics(BaseModel):
    """Performance and cost metrics."""
    latency_ms: int
    estimated_cost_usd: float


class AuditEntry(BaseModel):
    """Inline audit entry attached to a processed ticket."""
    audit_id: str
    timestamp: str
    decision_summary: str


class TicketProcessResponse(BaseModel):
    """Full response returned after processing a ticket."""
    ticket_id: str
    customer_id: str
    response_text: str
    memory: Memory
    sensitivity: Sensitivity
    routing: Routing
    metrics: Metrics
    audit: AuditEntry
