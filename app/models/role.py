from sqlalchemy import Column, BigInteger, String, Text, DateTime

from app.database.database import Base


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    role_name = Column(
        String(50),
        nullable=False
    )

    description = Column(
        Text
    )

    created_at = Column(
        DateTime
    )
    