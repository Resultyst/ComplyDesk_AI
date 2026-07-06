# ComplyDesk - AI Compliance Support Router

ComplyDesk is a compliance-aware AI support agent for high-performance fintech customer service. It automatically classifies incoming support tickets by compliance sensitivity, retrieves long-term customer memory from **Hindsight Cloud**, and routes the queries dynamically:
- **Low-sensitivity tickets** to cost-optimized cloud LLMs (**Groq** with `openai/gpt-oss-120b`).
- **Medium/High-sensitivity tickets** containing PII or regulatory compliance risks to local compliant hardware (**Ollama** running `llama3`), orchestrated via a **Cascadeflow-compatible** router adapter.

---

## Technical Stack & Integrations

- **Frontend**: Next.js 16 (App Router), TypeScript, Tailwind CSS
- **Backend**: Python FastAPI, Pydantic, Uvicorn
- **Persistent Memory**: [Hindsight Cloud](https://hindsight.vectorize.io) REST API (with local JSON fallback)
- **Cloud LLM Inference**: [Groq API](https://groq.com) (with automatic model deprecation fallback)
- **Local Compliant Inference**: [Ollama API](https://ollama.com) (for local on-device hardware)
- **Orchestration**: `CascadeflowRouterAdapter` featuring budget-aware routing, provider health tracking, and memory delta/influence extraction.

---

## Getting Started

### 1. Prerequisites
- Node.js 18+
- Python 3.10+
- Ollama installed locally

### 2. Configure Environment Variables
Copy `.env.example` to `.env` in the backend directory:
```bash
cp complydesk/backend/.env.example complydesk/backend/.env
```
Fill in the credentials:
- `HINDSIGHT_API_KEY`: Hindsight cloud key
- `GROQ_API_KEY`: Groq API key
- `OLLAMA_BASE_URL`: `http://localhost:11434` (Ollama base endpoint)

### 3. Start Local Compliant LLM (Ollama)
Ensure Ollama is running and pull the `llama3` model:
```bash
ollama pull llama3
```

### 4. Run the Backend (FastAPI)
```bash
cd complydesk/backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```
API Swagger documentation is accessible at: `http://localhost:8000/docs`

### 5. Run the Frontend (Next.js)
```bash
cd complydesk/frontend
npm install
npm run dev
```
Open `http://localhost:3000` to access the neobank compliance dashboard.

---

## Developer Demo Reset & Reseed Workflow

If you run multiple test tickets and want to wipe the session memory and restore the database to a clean, canonical demo state:

Run the single reset script:
```bash
cd complydesk/backend
python scripts/reset_demo_state.py
```
This script:
1. Wipes all cloud memory banks on **Hindsight Cloud** for the demo customers (`cust-001`, `cust-002`, `cust-003`, `cust-004`).
2. Reseeds Hindsight Cloud with the canonical preferences (e.g. email updates preferences, duplicate debit contexts).
3. Resets the local `audit_log.json` on disk to the 10 canonical support history audit logs.
4. Restart the FastAPI backend server to flush in-memory caches.

---

## Canonical 3-Ticket Demo Flow

To demonstrate the full power of ComplyDesk to judges, run these 3 support tickets in order in the `/workspace` composer:

### 1. Low Sensitivity (Cloud Route + Cost Optimization)
- **Customer**: Narayanan (`CUST-002`)
- **Ticket Text**: `"How long will my refund take for a cancelled card order?"`
- **What happens**: Sensitivity classified as `LOW`. Routed to **Groq Cloud**. Metrics show actual cloud cost (`$0.003`) matching baseline cost. Audit logs capture `[Compliance: False] [Budget: True]`.

### 2. High Sensitivity (Local Compliant Route + Memory Delta)
- **Customer**: Kumar (`CUST-004`)
- **Ticket Text**: `"My premium business card was charged twice again. Please send updates by email."`
- **What happens**: Sensitivity classified as `HIGH`. Routed to **Ollama** (`llama3`) locally. Memory delta indicates that the response is influenced by Kumar's previous duplicate debit report and email updates preference. actual cost is `$0.00` (free local hardware), saving `$0.05` compared to baseline secure cloud costs.

### 3. Medium Sensitivity (KYC Delay + Local Compliance)
- **Customer**: Santhosh (`CUST-003`)
- **Ticket Text**: `"My KYC verification is still pending even after I resubmitted the business documents."`
- **What happens**: Sensitivity classified as `MEDIUM` (PII involved). Routed to **Ollama** locally. Memory context acknowledges his prior manual KYC delay history, and routes cleanly at zero cost.
