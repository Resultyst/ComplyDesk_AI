from pydantic import BaseModel, ConfigDict


class AuditRecord(BaseModel):
    """Audit log record for compliance tracking."""
    model_config = ConfigDict(protected_namespaces=())
    audit_id: str
    timestamp: str
    ticket_id: str
    customer_id: str
    sensitivity: str
    model_selected: str
    routing_reason: str
    memory_used: bool
    latency_ms: int
    estimated_cost_usd: float
