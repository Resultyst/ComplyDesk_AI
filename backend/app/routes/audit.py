from fastapi import APIRouter

from app.schemas.audit import AuditRecord
from app.services import audit_service

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/", response_model=list[AuditRecord])
async def list_audit_records():
    """Return all audit log records."""
    return audit_service.list_audit_records()
