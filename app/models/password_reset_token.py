from sqlalchemy import (
    Column,
    BigInteger,
    Text,
    DateTime,
    ForeignKey
)

from app.database.database import Base


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    reset_token_id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id"),
        nullable=False
    )

    token = Column(
        Text,
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    used_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        nullable=False
    )