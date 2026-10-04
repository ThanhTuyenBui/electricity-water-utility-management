from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Text,
    DateTime,
    ForeignKey
)

from app.database.database import Base


class Customer(Base):

    __tablename__ = "customers"

    customer_id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        ForeignKey("users.user_id"),
        nullable=True
    )

    customer_code = Column(
        String(20),
        nullable=False
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    phone = Column(
        String(15),
        nullable=True
    )

    identity_number = Column(
        String(20),
        nullable=True
    )

    address = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    created_at = Column(
        DateTime,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        nullable=False
    )