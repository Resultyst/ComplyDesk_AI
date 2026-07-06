from pydantic import BaseModel


class Customer(BaseModel):
    """Core customer model."""
    customer_id: str
    name: str
    plan_tier: str
    preferred_channel: str
    account_type: str
    last_ticket_at: str
    email: str | None = None
    risk_profile: str | None = None


class MemoryItem(BaseModel):
    """A single memory item from Hindsight (mocked)."""
    key: str
    value: str
    source: str
    timestamp: str


class MemorySummary(BaseModel):
    """Aggregated memory summary for a customer."""
    total_interactions: int
    key_preferences: list[str]
    items: list[MemoryItem]


class TicketSummary(BaseModel):
    """Lightweight ticket info for customer detail views."""
    ticket_id: str
    subject: str
    status: str
    sensitivity: str
    created_at: str
    summary: str


class CustomerDetail(Customer):
    """Extended customer model with memory and recent tickets."""
    memory_summary: MemorySummary
    recent_tickets: list[TicketSummary]
