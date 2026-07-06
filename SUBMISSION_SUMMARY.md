# ComplyDesk - Hackathon Submission Summary

### One-Line Pitch
ComplyDesk is a compliance-aware, intelligent customer support router for neobanks that dynamically splits support traffic between secure on-premise hardware (Ollama) and cost-optimized cloud LLMs (Groq) while retaining persistent customer context via Hindsight Cloud.

---

### Problem Solved
1. **Regulated Compliance Friction**: In Indian fintech and neobanking (such as card payments, UPI transfers and account onboarding), support tickets containing PII, transaction details, or security warnings must strictly remain on-premise to comply with data residency and compliance audits.

2. **Context Loss**: Traditional support agents treat each ticket as a siloed transaction, repeating verification steps and ignoring past customer preferences (e.g. duplicate charges, onboarding delays, email-update preferences).

3. **High Cloud Costs**: Running massive cloud models for simple support tickets (e.g., card activation help or fee inquiries) is highly cost-inefficient.

4. **Audit trails**: Compliance officers lack granular transparency into how AI models make support decisions.

---

### How We Use Hindsight Cloud
ComplyDesk connects directly to **Hindsight Cloud** to retrieve and persist customer context:

- **Recall**: Prior to response generation, the orchestrator recalls past memories associated with the customer (e.g. previous billing disputes or UPI flags).

- **Consolidation**: During ticket processing, ComplyDesk extracts new memory-worthy facts, deduplicates and normalizes them, and writes them back to the customer's Hindsight memory bank.

- **English-Only Normalization**: Multilingual user text or previous foreign language inputs are automatically normalized and consolidated into structured English facts.

---

### How Groq / Ollama Routing Works
We use a custom, budget-aware **CascadeflowRouterAdapter** to split the workflow:

- **Low-Sensitivity**: Routed to **Groq Cloud** using the `openai/gpt-oss-120b` (or active fallback models) for maximum speed and cost efficiency (estimated at `$0.003` per ticket).

- **Medium/High-Sensitivity**: Automatically intercepted and routed to **Ollama** running `llama3:8b` locally on on-premise hardware to guarantee data protection. 

- **Resilience Fallbacks**: If Ollama or Groq is unreachable, the router automatically falls back to an offline rules-based backup engine to ensure the neobank platform never hangs.

---

### Key Differentiators
- **Persistent Context**: Uses memory delta analysis to prove that the generated response changed *because* it remembered the customer's prior ticket.

- **Dynamic Cost Savings**: Displays a live dashboard tracking total actual vs. baseline secure cloud costs, showing exact financial savings from local on-premise routing.

- **Provider Health Tracking**: A built-in health registry checks model loaded states before sending API requests, automatically bypassing degraded nodes.
