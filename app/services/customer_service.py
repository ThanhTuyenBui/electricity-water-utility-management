from sqlalchemy.orm import Session

from app.repositories.customer_service import (
    approve_customer_service as approve_customer_service_repo,
    register_customer_at_counter as register_customer_at_counter_repo
)

from app.core.security import hash_password


def approve_customer_service(
    db: Session,
    customer_service_id: int,
    admin_user_id: int
):
    return approve_customer_service_repo(
        db=db,
        customer_service_id=customer_service_id,
        admin_user_id=admin_user_id
    )


def register_customer_at_counter(
    db: Session,
    username: str,
    password: str,
    email: str,
    full_name: str,
    service_ids: list[int],
    employee_user_id: int,
    phone: str | None = None,
    identity_number: str | None = None,
    address: str | None = None
):
    # Hash password trước khi lưu vào database
    password_hash = hash_password(password)

    return register_customer_at_counter_repo(
        db=db,
        username=username,
        password_hash=password_hash,
        email=email,
        full_name=full_name,
        service_ids=service_ids,
        employee_user_id=employee_user_id,
        phone=phone,
        identity_number=identity_number,
        address=address
    )