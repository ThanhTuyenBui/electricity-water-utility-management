
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.security import (
    hash_password,
    verify_password
)

from app.repositories.auth import (
    register_customer as register_customer_repo
)


# ============================================================
# 1. ĐĂNG KÝ KHÁCH HÀNG
# ============================================================

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

    # 2. Gọi Repository lưu dữ liệu
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


# ============================================================
# 2. ĐỔI MẬT KHẨU
# ============================================================

def change_password_service(
    db: Session,
    user,
    old_password: str,
    new_password: str
):
    try:
        # 1. Lấy user_id
        user_id = getattr(user, "user_id", None)

        if user_id is None:
            raise ValueError(
                "Không tìm thấy thông tin tài khoản"
            )

        # 2. Lấy mật khẩu hiện tại bằng SQL thuần
        result = db.execute(
            text("""
                SELECT password_hash
                FROM users
                WHERE user_id = :user_id
            """),
            {
                "user_id": user_id
            }
        ).mappings().first()

        if not result:
            raise ValueError(
                "Không tìm thấy tài khoản"
            )

        current_password_hash = result["password_hash"]

        # 3. Kiểm tra mật khẩu cũ
        if not verify_password(
            old_password,
            current_password_hash
        ):
            raise ValueError(
                "Mật khẩu hiện tại không đúng"
            )

        # 4. Không cho sử dụng lại mật khẩu cũ
        if verify_password(
            new_password,
            current_password_hash
        ):
            raise ValueError(
                "Mật khẩu mới phải khác mật khẩu hiện tại"
            )

        # 5. Hash mật khẩu mới
        new_password_hash = hash_password(
            new_password
        )

        # 6. Cập nhật bằng SQL thuần
        db.execute(
            text("""
                UPDATE users
                SET password_hash = :password_hash
                WHERE user_id = :user_id
            """),
            {
                "password_hash": new_password_hash,
                "user_id": user_id
            }
        )

        # 7. Commit
        db.commit()

        return True

    except ValueError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise
