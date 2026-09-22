from sqlalchemy import Column, BigInteger, String, DateTime
from app.database.database import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(
        BigInteger,
        primary_key=True,
        index=True
    )

    user_id = Column(
        BigInteger,
        nullable=False
    )

    employee_code = Column(
        String(20),
        nullable=False,
        unique=True,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    phone = Column(
        String(15)
    )

    department = Column(
        String(100)
    )

    position = Column(
        String(100)
    )

    assigned_area = Column(
        String(100)
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