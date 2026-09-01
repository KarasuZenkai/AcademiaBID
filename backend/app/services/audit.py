import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.progress import AuditLog


def log_admin_action(session: Session, actor_id: uuid.UUID, action: str, entity_type: str, entity_id: uuid.UUID, details: Optional[dict] = None) -> None:
    session.add(AuditLog(actor_id=actor_id, action=action, entity_type=entity_type, entity_id=entity_id, details=details))
