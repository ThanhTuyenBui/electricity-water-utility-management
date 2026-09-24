from sqlalchemy.orm import Session

from app.repositories.customer_service import (
    approve_customer_service as approve_customer_service_repo,
    register_customer_at_counter as register_customer_at_counter_repo
)

from app.core.security import hash_password
from app.services.sms import SMSService

import secrets
import string


def generate_temporary_password(length: int = 10) -> str:
    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


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
    email: str,
    full_name: str,
    service_ids: list[int],
    employee_user_id: int,
    phone: str | None = None,
    identity_number: str | None = None,
    address: str | None = None
):
    # 1. Sinh mật khẩu tạm thời
    temporary_password = generate_temporary_password()

    # 2. Hash mật khẩu để lưu DB
    password_hash = hash_password(temporary_password)

    # 3. Tạo tài khoản khách hàng
    user_id = register_customer_at_counter_repo(
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

    # 4. Gửi Mock SMS
    if phone:
        sms_service = SMSService()

        sms_service.send_customer_password(
            phone_number=phone,
            username=username,
            password=temporary_password
        )

    # 5. Chỉ trả user_id
    return user_id