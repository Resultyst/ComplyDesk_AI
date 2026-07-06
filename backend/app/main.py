from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import customers, tickets, audit

app = FastAPI(
    title="ComplyDesk API",
    description="Compliance-aware AI support agent API for fintech",
    version="0.1.0",
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register route modules
app.include_router(customers.router)
app.include_router(tickets.router)
app.include_router(audit.router)


@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "complydesk-api"}
