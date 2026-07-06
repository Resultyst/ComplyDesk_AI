import logging
from app.schemas.customer import MemoryItem

logger = logging.getLogger(__name__)

# Dictionary-based translation mapping for multilingual demo records
TRANSLATION_MAP = {
    # Portuguese preference
    "o cliente prefere acompanhamento por e-mail": "Customer prefers email follow-up for dispute or fraud-related cases.",
    "o cliente prefere acompanhamento": "Customer prefers email follow-up for dispute or fraud-related cases.",
    # German duplicate debit
    "der kunde hat ein problem mit einer doppelten abbuchung": "Customer reported a duplicate debit issue on their business expense card.",
    "doppelten abbuchung": "Customer reported a duplicate debit issue on their business expense card.",
    # Spanish duplicate debit
    "el cliente reportó un problema de débito duplicado": "Customer reported a duplicate debit issue on their business expense card.",
    "el cliente reporto un problema": "Customer reported a duplicate debit issue on their business expense card.",
    # Portuguese duplicate debit
    "o cliente relatou um problema de débito duplicado": "Customer reported a duplicate debit issue on their business expense card.",
    "debito duplicado": "Customer reported a duplicate debit issue on their business expense card.",
    "débito duplicado": "Customer reported a duplicate debit issue on their business expense card.",
}

CATEGORY_MAP = {
    "customer_preference": "customer_preference",
    "customerpreference": "customer_preference",
    "support_history": "support_history",
    "supporthistory": "support_history",
    "compliance_context": "account_context",
    "compliancecontext": "account_context",
    "escalation_context": "risk_context",
    "escalationcontext": "risk_context",
    "general": "support_history",
    "account_context": "account_context",
    "risk_context": "risk_context",
}

def translate_to_english(value: str) -> str:
    """Normalize multilingual support memories into clean English equivalents."""
    val_lower = value.lower().strip()
    for key, english_val in TRANSLATION_MAP.items():
        if key in val_lower:
            return english_val
    return value

def normalize_category(category: str) -> str:
    """Map arbitrary categories to the 4 canonical categories."""
    cat = category.lower().strip().replace(" ", "_")
    return CATEGORY_MAP.get(cat, "support_history")

def get_concept_fingerprint(customer_id: str, category: str, value: str) -> str:
    """Generate a unique fingerprint for a specific customer concept to prevent duplicate facts."""
    val_clean = value.lower()
    concept = "general"
    
    if "email" in val_clean:
        concept = "email_pref"
    elif "chat" in val_clean:
        concept = "chat_pref"
    elif "kyc" in val_clean or "verification" in val_clean or "document" in val_clean:
        concept = "kyc_status"
    elif "debit" in val_clean or "charge" in val_clean:
        concept = "debit_dispute"
    elif "suspicious" in val_clean or "fraud" in val_clean or "unauthorized" in val_clean:
        concept = "fraud_risk"
    elif "restricted" in val_clean or "blocked" in val_clean or "locked" in val_clean:
        concept = "account_lock"

    return f"{customer_id.lower()}|{normalize_category(category)}|{concept}"

def filter_and_rank_memories(customer_id: str, items: list[MemoryItem], limit: int = 4) -> list[MemoryItem]:
    """Retrieve, clean, translate, deduplicate, and rank memories for prompt injection and UI."""
    seen_fingerprints = set()
    cleaned_items = []

    for item in items:
        # 1. Translate to English
        english_val = translate_to_english(item.value)
        # 2. Normalize Category
        canonical_cat = normalize_category(item.key)
        
        # 3. Generate concept fingerprint
        fp = get_concept_fingerprint(customer_id, canonical_cat, english_val)
        
        if fp not in seen_fingerprints:
            seen_fingerprints.add(fp)
            cleaned_items.append(MemoryItem(
                key=canonical_cat,
                value=english_val,
                source=item.source,
                timestamp=item.timestamp
            ))
            
    # 4. Rank items: customer_preference first, then support_history, then risk_context/account_context
    rank_order = {
        "customer_preference": 0,
        "support_history": 1,
        "risk_context": 2,
        "account_context": 3
    }
    
    cleaned_items.sort(key=lambda x: rank_order.get(x.key, 99))
    return cleaned_items[:limit]

def deduplicate_memories(
    existing_items: list[MemoryItem],
    new_facts: list
) -> list:
    """Deduplicate new facts against existing ones before writing to Hindsight."""
    unique_new_facts = []
    
    # Track existing fingerprints
    existing_fps = set()
    for ext in existing_items:
        ext_val = translate_to_english(ext.value)
        ext_cat = normalize_category(ext.key)
        fp = get_concept_fingerprint("temp", ext_cat, ext_val)
        existing_fps.add(fp)

    for fact in new_facts:
        fact_val = translate_to_english(fact.value)
        fact_cat = normalize_category(fact.key)
        fp = get_concept_fingerprint("temp", fact_cat, fact_val)
        
        if fp not in existing_fps:
            existing_fps.add(fp)
            # Create a normalized ExtractedMemory equivalent
            from app.services.memory_extraction_service import ExtractedMemory
            unique_new_facts.append(ExtractedMemory(
                key=fact_cat,
                value=fact_val,
                source=fact.source
            ))
            
    return unique_new_facts
