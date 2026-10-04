from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.core.config import settings


# Dùng Argon2 để mã hóa mật khẩu
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Mã hóa mật khẩu trước khi lưu vào database.
    """
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Kiểm tra mật khẩu người dùng nhập
    có khớp với mật khẩu đã mã hóa hay không.
    """
    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    user_id: int,
    username: str,
    role: str
) -> str:
    """
    Tạo JWT access token.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return token