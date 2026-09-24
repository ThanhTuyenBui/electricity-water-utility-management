import json

from sqlalchemy import text
from sqlalchemy.orm import Session


def log_audit_event(
    db: Session,
    user_id: int | None,
    action: str,
    table_name: str,
    record_id: int | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None
):
    query = text("""
        SELECT log_audit_event(
            :user_id,
            :action,
            :table_name,
            :record_id,
            CAST(:old_value AS JSONB),
            CAST(:new_value AS JSONB)
        )
    """)

    db.execute(
        query,
        {
            "user_id": user_id,
            "action": action,
            "table_name": table_name,
            "record_id": record_id,
            "old_value": json.dumps(old_value) if old_value is not None else None,
            "new_value": json.dumps(new_value) if new_value is not None else None
        }
    )

    db.commit()