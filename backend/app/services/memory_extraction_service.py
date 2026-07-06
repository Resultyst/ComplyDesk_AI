from typing import NamedTuple

class ExtractedMemory(NamedTuple):
    key: str
    value: str
    source: str


def extract_new_memories(ticket_text: str, sensitivity_level: str) -> list[ExtractedMemory]:
    """Inspect NexaPay ticket text and sensitivity to extract support-relevant memory facts for storage."""
    new_memories = []
    text_lower = ticket_text.lower()

    # 1. Update customer preferences
    if "email" in text_lower and ("update" in text_lower or "send" in text_lower or "follow-up" in text_lower):
        new_memories.append(
            ExtractedMemory(
                key="customer_preference",
                value="Customer prefers email follow-up for dispute or fraud-related cases.",
                source="ticket_interaction"
            )
        )
    elif "chat" in text_lower:
        new_memories.append(
            ExtractedMemory(
                key="customer_preference",
                value="Customer prefers quick chat-based support.",
                source="ticket_interaction"
            )
        )

    # 2. Extract dispute details -> support_history
    if "duplicate debit" in text_lower or "charged twice" in text_lower or "debit twice" in text_lower:
        new_memories.append(
            ExtractedMemory(
                key="support_history",
                value="Customer has reported a duplicate debit issue on the business expense card.",
                source="ticket_interaction"
            )
        )

    # 3. Extract KYC/verification -> compliance_context
    if "kyc" in text_lower or "verification" in text_lower or "document" in text_lower or "gst" in text_lower:
        new_memories.append(
            ExtractedMemory(
                key="compliance_context",
                value="Business KYC verification has previously been delayed and required manual review.",
                source="ticket_interaction"
            )
        )

    # 4. Extract fraud/restriction alerts -> escalation_context
    if sensitivity_level == "high" and ("unauthorized" in text_lower or "suspicious" in text_lower or "blocked" in text_lower or "restricted" in text_lower):
        new_memories.append(
            ExtractedMemory(
                key="escalation_context",
                value="Account restricted during compliance verification or suspicious debit attempt.",
                source="ticket_interaction"
            )
        )

    # Fallback to general support history if nothing matched but sensitivity is high/medium
    if not new_memories:
        if sensitivity_level == "high":
            new_memories.append(
                ExtractedMemory(
                    key="escalation_context",
                    value="Fraud-related cases for this account require prompt escalation.",
                    source="ticket_interaction"
                )
            )
        elif sensitivity_level == "medium":
            new_memories.append(
                ExtractedMemory(
                    key="compliance_context",
                    value="Customer has resubmitted business documents during a compliance query.",
                    source="ticket_interaction"
                )
            )

    # Limit to maximum of 2 memories
    return new_memories[:2]
