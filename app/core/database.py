
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


# ============================================================
# 1. KẾT NỐI DATABASE
# ============================================================

engine = create_engine(settings.DATABASE_URL)


# ============================================================
# 2. CUSTOM SESSION CHO AUDIT LOG
# ============================================================

class AuditSession(Session):
    """
    Session mở rộng để lưu thông tin người thực hiện request.
    """


@event.listens_for(AuditSession, "after_begin")
def set_audit_context(session, transaction, connection):
    """
    Tự động thiết lập user_id cho PostgreSQL
    mỗi khi transaction bắt đầu.
    """

    user_id = session.info.get("audit_user_id")

    connection.execute(
        text("""
            SELECT set_config(
                'app.user_id',
                :user_id,
                true
            )
        """),
        {
            "user_id": str(user_id) if user_id is not None else ""
        }
    )


# ============================================================
# 3. SESSION LOCAL
# ============================================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AuditSession
)
