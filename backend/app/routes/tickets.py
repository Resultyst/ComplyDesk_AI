from fastapi import APIRouter

from app.schemas.ticket import TicketProcessRequest, TicketProcessResponse
from app.services import ticket_orchestrator

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/process", response_model=TicketProcessResponse)
async def process_ticket(request: TicketProcessRequest):
    """Process a support ticket through the AI pipeline."""
    return ticket_orchestrator.process_ticket(request)
