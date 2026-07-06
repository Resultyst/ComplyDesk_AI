from app.repositories import audit_repo
from app.schemas.audit import AuditRecord


def list_audit_records() -> list[AuditRecord]:
    """Return all audit records."""
    raw = audit_repo.get_all_audit_records()
    return [AuditRecord(**r) for r in raw]
