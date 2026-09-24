from sqlalchemy.orm import Session

from app.repositories.audit_log import (
    log_audit_event as log_audit_event_repo
)


def log_audit_event(
    db: Session,
    user_id: int | None,
    action: str,
    table_name: str,
    record_id: int | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None
):
    return log_audit_event_repo(
        db=db,
        user_id=user_id,
        action=action,
        table_name=table_name,
        record_id=record_id,
        old_value=old_value,
        new_value=new_value
    )