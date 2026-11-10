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


from sqlalchemy.orm import Session
from sqlalchemy import text


def set_audit_context(
    db: Session,
    current_user,
    ip_address: str = None
):
    """
    Truyền thông tin người thực hiện xuống PostgreSQL.
    Các giá trị chỉ tồn tại trong transaction hiện tại.
    """

    user_id = getattr(current_user, "user_id", None)

    db.execute(
        text("""
            SELECT
                set_config(
                    'app.user_id',
                    :user_id,
                    TRUE
                ),
                set_config(
                    'app.ip_address',
                    :ip_address,
                    TRUE
                )
        """),
        {
            "user_id": str(user_id) if user_id is not None else "",
            "ip_address": ip_address or ""
        }
    )
