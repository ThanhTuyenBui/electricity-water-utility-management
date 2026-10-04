from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime
)

from sqlalchemy.dialects.postgresql import JSONB

from app.database.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    log_id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        nullable=True
    )

    action = Column(
        String(100),
        nullable=False
    )

    table_name = Column(
        String(100)
    )

    record_id = Column(
        BigInteger
    )

    old_value = Column(
        JSONB
    )

    new_value = Column(
        JSONB
    )

    created_at = Column(
        DateTime
    )