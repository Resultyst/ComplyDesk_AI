from app.schemas.ticket import Sensitivity

# Trigger word mapping to (Level, Tag, Description)
# Checked in order of severity
HIGH_TRIGGERS = [
    ("unauthorized transaction", "fraud_risk", "unauthorized transaction report"),
    ("unauthorized withdrawal", "fraud_risk", "unauthorized withdrawal report"),
    ("unauthorized", "fraud_risk", "unauthorized activity reported"),
    ("duplicate debit", "billing_dispute", "duplicate transaction debit"),
    ("card charged twice", "billing_dispute", "duplicate card charge dispute"),
    ("charged twice", "billing_dispute", "duplicate charge dispute"),
    ("suspicious debit", "fraud_risk", "suspicious debit alert"),
    ("suspicious login", "fraud_risk", "suspicious login attempt alert"),
    ("suspicious transaction", "fraud_risk", "suspicious transaction alert"),
    ("payouts are blocked", "fraud_risk", "restricted outgoing payments"),
    ("restricted", "fraud_risk", "security-related account restriction"),
    ("blocked", "fraud_risk", "security-related account freeze"),
    ("chargeback", "billing_dispute", "chargeback log request"),
    ("ach dispute", "billing_dispute", "ACH bank dispute request"),
    ("card ending", "card_reference", "specific payment card reference"),
    ("account number", "card_reference", "sensitive account identifier reference"),
    ("transaction id", "card_reference", "transaction ID reference"),
    ("txn id", "card_reference", "transaction ID reference"),
]

# Medium triggers map to PII or account-specific finance alerts without fraud
MEDIUM_TRIGGERS = [
    ("kyc verification pending", "kyc_issue", "KYC verification delays"),
    ("kyc verification", "kyc_issue", "KYC verification status review"),
    ("kyc", "kyc_issue", "KYC onboarding query"),
    ("verification", "kyc_issue", "Aadhaar/PAN document verification inquiry"),
    ("payout refund", "refund_request", "failed payout fee refund request"),
    ("failed payout fee", "refund_request", "failed payout fee dispute"),
    ("flagged as suspicious", "fraud_risk", "false risk flag hold dispute"),
    ("flagged incorrectly", "fraud_risk", "incorrect risk hold dispute"),
    ("flagged", "fraud_risk", "transaction hold check"),
    ("billing cycle", "account_update", "billing cycle registration check"),
    ("processing fee", "payment_issue", "fee review request"),
    ("fee refund", "refund_request", "fee waiver or refund request"),
    ("settlement not received", "payment_issue", "delayed merchant settlement payout"),
    ("vendor payout settlement", "payment_issue", "delayed NEFT/IMPS payout transfer"),
]

# Low triggers map to generic FAQs, card deliveries, and virtual card setups
LOW_TRIGGERS = [
    ("refund timeline", "refund_request", "general refund timeline policy"),
    ("virtual card activation", "upi_issue", "virtual card setup instructions"),
    ("virtual card", "upi_issue", "virtual card configuration check"),
    ("transfer limit", "general_support", "payout transaction limits inquiry"),
    ("limit clarification", "general_support", "transaction limits inquiry"),
    ("email update", "account_update", "change registered email address"),
    ("registered business email", "account_update", "update registered corporate email"),
    ("registered email", "account_update", "update registered email"),
    ("delivery status", "general_support", "physical card delivery status"),
    ("general support", "general_support", "generic help request"),
    ("faq", "general_support", "FAQ search"),
    ("preferences", "account_update", "customer communication settings update"),
]


def classify_sensitivity(text: str) -> Sensitivity:
    """Evaluate NexaPay ticket text against deterministic triggers to return sensitivity data."""
    text_lower = text.lower()
    risk_tags = set()

    # Check High Triggers
    high_matches = []
    for trigger, tag, desc in HIGH_TRIGGERS:
        if trigger in text_lower:
            high_matches.append(trigger)
            risk_tags.add(tag)
    if high_matches:
        reasoning = f"NexaPay Security Engine flagged HIGH sensitivity due to: {', '.join(high_matches)} ({desc})."
        return Sensitivity(
            level="high",
            risk_tags=list(risk_tags),
            reasoning=reasoning
        )

    # Check Medium Triggers
    medium_matches = []
    for trigger, tag, desc in MEDIUM_TRIGGERS:
        if trigger in text_lower:
            medium_matches.append(trigger)
            risk_tags.add(tag)
    if medium_matches:
        reasoning = f"NexaPay Compliance Engine flagged MEDIUM sensitivity due to: {', '.join(medium_matches)} ({desc})."
        return Sensitivity(
            level="medium",
            risk_tags=list(risk_tags),
            reasoning=reasoning
        )

    # Check Low Triggers
    low_matches = []
    for trigger, tag, desc in LOW_TRIGGERS:
        if trigger in text_lower:
            low_matches.append(trigger)
            risk_tags.add(tag)
    if low_matches:
        reasoning = f"NexaPay Support Engine classified LOW sensitivity due to: {', '.join(low_matches)}."
        return Sensitivity(
            level="low",
            risk_tags=list(risk_tags),
            reasoning=reasoning
        )

    # Default fallback
    return Sensitivity(
        level="low",
        risk_tags=["general_support"],
        reasoning="No specific NexaPay compliance, financial dispute, or safety triggers detected. Routed to cost-optimized queue."
    )
