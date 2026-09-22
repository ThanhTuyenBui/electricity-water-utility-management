from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.repositories.auth import register_customer as register_customer_repo


def register_customer(
    db: Session,
    username: str,
    password: str,
    email: str,
    full_name: str,
    service_ids: list[int],
    phone: str | None = None,
    identity_number: str | None = None,
    address: str | None = None
):
    # 1. Hash password
    password_hash = hash_password(password)

    # 2. Gọi Repository để lưu xuống database
    user_id = register_customer_repo(
        db=db,
        username=username,
        password_hash=password_hash,
        email=email,
        full_name=full_name,
        service_ids=service_ids,
        phone=phone,
        identity_number=identity_number,
        address=address
    )

    return user_id