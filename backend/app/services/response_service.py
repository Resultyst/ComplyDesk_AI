from app.schemas.customer import MemoryItem

def generate_response(
    customer_name: str,
    preferred_channel: str,
    memory_items: list[MemoryItem],
    sensitivity_level: str,
    risk_tags: list[str],
    ticket_text: str
) -> str:
    """Generate a highly professional, deterministic NexaPay customer support response

    incorporating customer preferences, prior issues, and sensitivity requirements.
    """
    ticket_text_lower = ticket_text.lower()
    
    # 1. Classify the query type
    is_refund_timeline = "refund" in ticket_text_lower and any(kw in ticket_text_lower for kw in ["timeline", "how long", "when will", "days", "time"])
    is_refund_general = "refund" in ticket_text_lower or "fee" in ticket_text_lower
    is_kyc = any(kw in ticket_text_lower for kw in ["kyc", "verification", "document", "pan", "gst", "gstin", "aadhaar"])
    is_fraud_or_dispute = any(kw in ticket_text_lower for kw in ["unauthorized", "fraud", "debit", "suspicious", "charge", "blocked", "restricted", "freeze"])

    # 2. Check memory for prior history
    has_prior_duplicate_debit = any("duplicate debit" in item.value.lower() for item in memory_items)
    has_prior_kyc_delay = any("kyc" in item.value.lower() or "verification" in item.value.lower() for item in memory_items)
    has_prior_suspicious_debit = any("suspicious debit" in item.value.lower() or "monitored" in item.value.lower() for item in memory_items)
    prefers_email_disputes = any("email" in item.value.lower() and ("dispute" in item.value.lower() or "compliance" in item.value.lower()) for item in memory_items)

    history_ack = ""
    if is_fraud_or_dispute and has_prior_duplicate_debit:
        history_ack = "We note that you have previously reported a duplicate debit issue on your NexaPay expense card. Our dispute resolution team is cross-referencing this with our banking processor."
    elif is_fraud_or_dispute and has_prior_suspicious_debit:
        history_ack = "As your NexaPay account was previously flagged for security monitoring following a suspicious debit attempt, we are treating this security ticket with maximum compliance priority."
    elif is_kyc and has_prior_kyc_delay:
        history_ack = "We recognize your business profile has experienced manual KYC verification delays and document resubmissions in earlier cases. We are expediting this review."

    # 3. Formulate the core support response based on query type & sensitivity
    if sensitivity_level == "high":
        main_message = (
            f"Dear {customer_name}, we have detected urgent security indicators regarding your NexaPay account. "
            "For your safety, we have locked additional withdrawals on your profile and escalated this case directly "
            "to our Fraud & Risk Operations department for manual review."
        )
    elif sensitivity_level == "medium":
        if is_kyc:
            main_message = (
                f"Dear {customer_name}, your business KYC verification inquiry has been successfully queued. "
                "Because this concerns official onboarding credentials, our compliance officers are manually verifying "
                "your uploaded registry documents to resolve the pending status."
            )
        else:
            main_message = (
                f"Dear {customer_name}, I have opened a dispute review for the transaction discrepancy on your NexaPay wallet. "
                "A reconciliation request has been logged with our clearing bank partner to trace these funds."
            )
    else:
        # Low sensitivity scenarios
        if is_refund_timeline:
            main_message = (
                f"Dear {customer_name}, standard refund processing on NexaPay takes between 5 to 7 working days to reflect "
                "in your source account, depending on your bank's settlement cycle."
            )
        elif "virtual card" in ticket_text_lower:
            main_message = (
                f"Dear {customer_name}, your NexaPay virtual card is immediately ready for online use. "
                "You can toggle transaction limits and view card details under the 'Cards' tab in your mobile app."
            )
        elif "limit" in ticket_text_lower:
            main_message = (
                f"Dear {customer_name}, same-day beneficiary payout transfer limits are determined by your account tier "
                "and NPCI regulations. You can check current limits and applicable KYC checks in the portal dashboard."
            )
        else:
            main_message = (
                f"Dear {customer_name}, thank you for contacting NexaPay Support. We have received your query and "
                "our customer success team is looking into the details."
            )

    # 4. Formulate channel response updates
    channel_update = ""
    # Check if they request updates in the current ticket text or prefer email for disputes
    requests_email_updates = "email" in ticket_text_lower or preferred_channel.lower() == "email" or prefers_email_disputes
    
    if requests_email_updates:
        channel_update = "We will send detailed progress logs directly to your registered email address as preferred."
    elif preferred_channel.lower() == "chat":
        channel_update = "Please keep this chat session active. A support associate will join this thread shortly."
    else:
        channel_update = "We will follow up with you shortly via your preferred support channel."

    # Combine response parts
    parts = [main_message]
    if history_ack:
        parts.append(history_ack)
    parts.append(channel_update)

    return " ".join(parts)
