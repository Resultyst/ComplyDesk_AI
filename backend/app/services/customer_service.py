from typing import Optional

from app.repositories import customer_repo, ticket_repo
from app.schemas.customer import (
    Customer,
    CustomerDetail,
    MemoryItem,
    MemorySummary,
    TicketSummary,
)


from app.services.memory_provider import get_memory_provider

def list_customers() -> list[Customer]:
    """Return all customers."""
    raw = customer_repo.get_all_customers()
    return [Customer(**c) for c in raw]


def get_customer_detail(customer_id: str) -> Optional[CustomerDetail]:
    """Return full customer detail with memory and recent tickets."""
    raw = customer_repo.get_customer_by_id(customer_id)
    if raw is None:
        return None

    # Retrieve real memory items via active memory provider
    memory_provider = get_memory_provider()
    memory_items = memory_provider.get_memory_items(customer_id)

    # Compile key preferences dynamically
    key_preferences = [
        f"Prefers {raw['preferred_channel']} communication",
        f"Registered account type is {raw['account_type']}",
    ]
    for item in memory_items:
        if "history" in item.key or "pref" in item.key:
            key_preferences.append(item.value)

    # Get recent tickets for this customer
    raw_tickets = ticket_repo.get_tickets_by_customer(customer_id)
    recent_tickets = [TicketSummary(**t) for t in raw_tickets]

    memory_summary = MemorySummary(
        total_interactions=len(memory_items) + len(recent_tickets),
        key_preferences=key_preferences[:4], # limit to top 4 preferences
        items=memory_items,
    )

    return CustomerDetail(
        **raw,
        memory_summary=memory_summary,
        recent_tickets=recent_tickets,
    )
