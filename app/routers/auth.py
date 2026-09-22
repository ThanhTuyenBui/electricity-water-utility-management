from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.v1 import Field
from sqlalchemy.orm import Session
import secrets
from datetime import datetime, timedelta

from app.core.dependencies import (
    get_db,
    get_current_user
)
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.models.user import User
from app.models.role import Role
from app.models.password_reset_token import PasswordResetToken
from app.services.email_service import send_reset_password_email
from app.services.auth import register_customer
from app.schemas.auth import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
    ResetPasswordRequest
)


router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    user_id = register_customer(
        db=db,
        username=data.username,
        password=data.password,
        email=data.email,
        full_name=data.full_name,
        phone=data.phone,
        identity_number=data.identity_number,
        address=data.address,
        service_ids=data.service_ids
    )

    user = db.query(User).filter(
        User.user_id == user_id
    ).first()

    return user

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Đăng nhập bằng username + password.
    """

    # 1. Tìm user
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    # 2. Không tìm thấy user
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username hoặc password không đúng",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # 3. Kiểm tra password
    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username hoặc password không đúng",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # 4. Kiểm tra trạng thái tài khoản
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động"
        )

    # 5. Lấy role
    role = (
        db.query(Role)
        .filter(Role.role_id == user.role_id)
        .first()
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa được phân quyền"
        )

    # 6. Tạo JWT
    access_token = create_access_token(
        user_id=user.user_id,
        username=user.username,
        role=role.role_name
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user
@router.post("/forgot-password")
def forgot_password(
    username: str,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.username == username)
        .first()
    )

    # Không tiết lộ tài khoản có tồn tại hay không
    if user is None:
        return {
            "message": "Nếu tài khoản tồn tại, email đặt lại mật khẩu đã được gửi"
        }

    # Kiểm tra tài khoản có email hay chưa
    if not user.email:
        return {
            "message": "Nếu tài khoản tồn tại, email đặt lại mật khẩu đã được gửi"
        }

    # Tạo token ngẫu nhiên
    raw_token = secrets.token_urlsafe(32)

    # Tạo bản ghi yêu cầu đặt lại mật khẩu
    reset_token = PasswordResetToken(
        user_id=user.user_id,
        token=raw_token,
        expires_at=datetime.now() + timedelta(minutes=15),
        created_at=datetime.now()
    )

    db.add(reset_token)
    db.commit()

    # Gửi email
    send_reset_password_email(
        to_email=user.email,
        reset_token=raw_token
    )

    return {
        "message": "Nếu tài khoản tồn tại, email đặt lại mật khẩu đã được gửi"
    }    
@router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    reset_token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token == data.token,
            PasswordResetToken.used_at.is_(None)
        )
        .first()
    )

    if reset_token is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token không hợp lệ hoặc đã được sử dụng"
        )

    # Kiểm tra token hết hạn
    if reset_token.expires_at < datetime.now():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token đã hết hạn"
        )

    # Tìm tài khoản
    user = (
        db.query(User)
        .filter(User.user_id == reset_token.user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản"
        )

    # Đổi mật khẩu
    user.password_hash = hash_password(
        data.new_password
    )

    user.updated_at = datetime.now()

    # Đánh dấu token đã sử dụng
    reset_token.used_at = datetime.now()

    db.commit()

    return {
        "message": "Đặt lại mật khẩu thành công"
    }