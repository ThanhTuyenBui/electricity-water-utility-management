from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Form
)
from app.services.audit_log import log_audit_event
from fastapi.security import OAuth2PasswordRequestForm

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


# =========================================================
# REGISTER
# =========================================================

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

    # Ghi audit đăng ký tài khoản
    log_audit_event(
        db=db,
        user_id=user_id,
        action="REGISTER",
        table_name="users",
        record_id=user_id,
        new_value={
            "username": data.username,
            "email": data.email,
            "full_name": data.full_name
        }
    )

    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    return user


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.username == form_data.username)
        .first()
    )

    # Không tìm thấy username
    if user is None:
        return_error = True

        log_audit_event(
            db=db,
            user_id=None,
            action="LOGIN_FAILED",
            table_name="users",
            record_id=None,
            new_value={
                "username": form_data.username,
                "reason": "USER_NOT_FOUND"
            }
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username hoặc password không đúng",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Sai password
    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        log_audit_event(
            db=db,
            user_id=user.user_id,
            action="LOGIN_FAILED",
            table_name="users",
            record_id=user.user_id,
            new_value={
                "reason": "INVALID_PASSWORD"
            }
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username hoặc password không đúng",
            headers={
                "WWW-Authenticate": "Bearer"
            }
        )

    # Tài khoản không hoạt động
    if user.status != "ACTIVE":
        log_audit_event(
            db=db,
            user_id=user.user_id,
            action="LOGIN_FAILED",
            table_name="users",
            record_id=user.user_id,
            new_value={
                "reason": "INACTIVE_ACCOUNT"
            }
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động"
        )

    role = (
        db.query(Role)
        .filter(Role.role_id == user.role_id)
        .first()
    )

    if role is None:
        log_audit_event(
            db=db,
            user_id=user.user_id,
            action="LOGIN_FAILED",
            table_name="users",
            record_id=user.user_id,
            new_value={
                "reason": "ROLE_NOT_FOUND"
            }
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản chưa được phân quyền"
        )

    # Tạo JWT
    access_token = create_access_token(
        user_id=user.user_id,
        username=user.username,
        role=role.role_name
    )

    # Ghi audit đăng nhập thành công
    log_audit_event(
        db=db,
        user_id=user.user_id,
        action="LOGIN",
        table_name="users",
        record_id=user.user_id,
        new_value={
            "username": user.username,
            "role": role.role_name
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
# =========================================================
# GET CURRENT USER
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse
)
def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post("/forgot-password")
def forgot_password(
    username: str = Form(...),
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
            "message": (
                "Nếu tài khoản tồn tại, "
                "email đặt lại mật khẩu đã được gửi"
            )
        }

    if not user.email:
        return {
            "message": (
                "Nếu tài khoản tồn tại, "
                "email đặt lại mật khẩu đã được gửi"
            )
        }

    # Tạo token ngẫu nhiên
    raw_token = secrets.token_urlsafe(32)

    # Lưu token vào database
    reset_token = PasswordResetToken(
        user_id=user.user_id,
        token=raw_token,
        expires_at=datetime.now() + timedelta(minutes=15),
        created_at=datetime.now()
    )

    db.add(reset_token)
    db.commit()

    # Gửi token qua Gmail SMTP
    send_reset_password_email(
        to_email=user.email,
        reset_token=raw_token
    )

    # Ghi audit sau khi gửi email thành công
    log_audit_event(
        db=db,
        user_id=user.user_id,
        action="FORGOT_PASSWORD",
        table_name="users",
        record_id=user.user_id,
        new_value={
            "username": user.username,
            "email": user.email
        }
    )

    return {
        "message": (
            "Nếu tài khoản tồn tại, "
            "email đặt lại mật khẩu đã được gửi"
        )
    }


# =========================================================
# RESET PASSWORD
# =========================================================

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

    user = (
        db.query(User)
        .filter(
            User.user_id == reset_token.user_id
        )
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy tài khoản"
        )

    # Hash password mới
    user.password_hash = hash_password(
        data.new_password
    )

    user.updated_at = datetime.now()

    # Đánh dấu token đã sử dụng
    reset_token.used_at = datetime.now()

    db.commit()

    # Ghi audit đặt lại mật khẩu
    log_audit_event(
        db=db,
        user_id=user.user_id,
        action="RESET_PASSWORD",
        table_name="users",
        record_id=user.user_id,
        new_value={
            "username": user.username
        }
    )

    return {
        "message": "Đặt lại mật khẩu thành công"
    }