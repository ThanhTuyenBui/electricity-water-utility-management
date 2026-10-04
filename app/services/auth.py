from sqlalchemy.orm import Session

from app.core.security import ( hash_password, verify_password )
from app.repositories.auth import register_customer as register_customer_repo
from app.models.user import User

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

def change_password_service(
    db: Session,
    user: User,
    old_password: str,
    new_password: str
):
    # Kiểm tra mật khẩu cũ
    if not verify_password(
        old_password,
        user.password_hash
    ):
        raise ValueError(
            "Mật khẩu hiện tại không đúng"
        )

    # Không cho dùng lại mật khẩu cũ
    if verify_password(
        new_password,
        user.password_hash
    ):
        raise ValueError(
            "Mật khẩu mới phải khác mật khẩu hiện tại"
        )

    # Hash mật khẩu mới
    user.password_hash = hash_password(
        new_password
    )

    db.commit()

    return True
