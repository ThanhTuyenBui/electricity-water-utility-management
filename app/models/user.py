from sqlalchemy import (
    Column,
    BigInteger,
    String,
    DateTime,
    ForeignKey
)

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    username = Column(
        String(50),
        nullable=False,
        unique=True,
        index=True
    )

    
    email = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )
    
    password_hash = Column(
        String(255),
        nullable=False
    )

    role_id = Column(
        BigInteger,
        ForeignKey("roles.role_id"),
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False
    )

    created_at = Column(
        DateTime
    )

    updated_at = Column(
        DateTime
    )
