
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
    Form
)
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import text
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

from app.services.audit_log import log_audit_event

from app.services.email_service import send_reset_password_email

from app.services.auth import (
    register_customer,
    change_password_service
)

from app.schemas.auth import (
    RegisterRequest,
    TokenResponse,
    UserResponse,
    ResetPasswordRequest,
    ChangePasswordRequest
)


router = APIRouter()


async def extract_login_credentials(request: Request):
    """Hỗ trợ cả form-data và JSON, đồng thời chấp nhận tên trường tiếng Việt."""
    content_type = request.headers.get("content-type", "").lower()

    if "application/json" in content_type:
        payload = await request.json()
        username = payload.get("username") or payload.get("ten_dang_nhap")
        password = payload.get("password") or payload.get("mat_khau")
        return username, password

    form_data = await request.form()
    username = form_data.get("username") or form_data.get("ten_dang_nhap")
    password = form_data.get("password") or form_data.get("mat_khau")
    return username, password


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
    try:
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

        # Lấy thông tin user bằng SQL thuần
        result = db.execute(
            text("""
                SELECT
                    user_id,
                    username,
                    role_id,
                    status,
                    email
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        )

        user = result.mappings().first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy tài khoản vừa đăng ký"
            )

        return dict(user)

    except HTTPException:
        db.rollback()
        raise

    except Exception as e:
        db.rollback()

        error_message = str(e)

        if "Tên đăng nhập đã tồn tại" in error_message:
            detail = "Tên đăng nhập đã tồn tại. Vui lòng chọn username khác."

        elif "Email không đúng định dạng" in error_message:
            detail = "Email không đúng định dạng. Vui lòng nhập lại."

        elif "Email đã được sử dụng" in error_message:
            detail = "Email đã tồn tại. Vui lòng sử dụng email khác."

        elif "Số điện thoại phải gồm 10 chữ số" in error_message:
            detail = "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0."

        elif "Số điện thoại đã được sử dụng" in error_message:
            detail = "Số điện thoại đã tồn tại. Vui lòng sử dụng số khác."

        elif "Số định danh cá nhân phải gồm đúng 12 chữ số" in error_message:
            detail = "Số định danh cá nhân phải gồm đúng 12 chữ số."

        elif "Số định danh cá nhân đã được sử dụng" in error_message:
            detail = "Số định danh cá nhân đã tồn tại."

        elif "Phải chọn ít nhất một dịch vụ" in error_message:
            detail = "Vui lòng chọn ít nhất một dịch vụ."

        elif "Mã dịch vụ không hợp lệ" in error_message:
            detail = "Dịch vụ được chọn không tồn tại hoặc không hợp lệ."

        elif "dịch vụ trùng nhau" in error_message:
            detail = "Không được chọn trùng dịch vụ."

        else:
            detail = error_message

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse
)
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    username, password = await extract_login_credentials(request)

    if username is None or password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập và mật khẩu không được để trống"
        )

    username = str(username).strip()
    password = str(password)

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tên đăng nhập và mật khẩu không được để trống"
        )

    result = db.execute(
        text("""
            SELECT
                u.user_id,
                u.username,
                u.password_hash,
                u.role_id,
                u.status,
                r.role_name
            FROM users u
            LEFT JOIN roles r
                ON u.role_id = r.role_id
            WHERE u.username = :username
        """),
        {"username": username}
    )

    user = result.mappings().first()

    # Không tìm thấy username
    if user is None:
        log_audit_event(
            db=db,
            user_id=None,
            action="LOGIN_FAILED",
            table_name="users",
            record_id=None,
            new_value={
                "username": username,
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
        password,
        user["password_hash"]
    ):
        log_audit_event(
            db=db,
            user_id=user["user_id"],
            action="LOGIN_FAILED",
            table_name="users",
            record_id=user["user_id"],
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
    if user["status"] != "ACTIVE":
        log_audit_event(
            db=db,
            user_id=user["user_id"],
            action="LOGIN_FAILED",
            table_name="users",
            record_id=user["user_id"],
            new_value={
                "reason": "INACTIVE_ACCOUNT"
            }
        )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động"
        )

    # Không tìm thấy role
    if user["role_name"] is None:
        log_audit_event(
            db=db,
            user_id=user["user_id"],
            action="LOGIN_FAILED",
            table_name="users",
            record_id=user["user_id"],
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
        user_id=user["user_id"],
        username=user["username"],
        role=user["role_name"]
    )

    # Ghi audit đăng nhập thành công
    log_audit_event(
        db=db,
        user_id=user["user_id"],
        action="LOGIN",
        table_name="users",
        record_id=user["user_id"],
        new_value={
            "username": user["username"],
            "role": user["role_name"]
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
    current_user=Depends(get_current_user)
):
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "role_id": current_user.role_id,
        "status": current_user.status,
        "email": getattr(current_user, "email", None)
    }


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post("/forgot-password")
def forgot_password(
    username: str = Form(...),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""
            SELECT
                user_id,
                username,
                email
            FROM users
            WHERE username = :username
        """),
        {"username": username}
    )

    user = result.mappings().first()

    # Không tiết lộ tài khoản có tồn tại hay không
    if user is None or not user["email"]:
        return {
            "message": (
                "Nếu tài khoản tồn tại, "
                "email đặt lại mật khẩu đã được gửi"
            )
        }

    # Tạo token ngẫu nhiên
    raw_token = secrets.token_urlsafe(32)

    now = datetime.now()
    expires_at = now + timedelta(minutes=15)

    try:
        # Lưu token bằng SQL thuần
        db.execute(
            text("""
                INSERT INTO password_reset_tokens (
                    user_id,
                    token,
                    expires_at,
                    created_at
                )
                VALUES (
                    :user_id,
                    :token,
                    :expires_at,
                    :created_at
                )
            """),
            {
                "user_id": user["user_id"],
                "token": raw_token,
                "expires_at": expires_at,
                "created_at": now
            }
        )

        db.commit()

    except Exception:
        db.rollback()
        raise

    # Gửi token qua Gmail SMTP
    send_reset_password_email(
        to_email=user["email"],
        reset_token=raw_token
    )

    # Ghi audit sau khi gửi email thành công
    log_audit_event(
        db=db,
        user_id=user["user_id"],
        action="FORGOT_PASSWORD",
        table_name="users",
        record_id=user["user_id"],
        new_value={
            "username": user["username"],
            "email": user["email"]
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
    now = datetime.now()

    try:
        # Tìm token chưa sử dụng
        result = db.execute(
            text("""
                SELECT
                    user_id,
                    token,
                    expires_at,
                    used_at
                FROM password_reset_tokens
                WHERE token = :token
                  AND used_at IS NULL
                LIMIT 1
            """),
            {"token": data.token}
        )

        reset_token = result.mappings().first()

        if reset_token is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token không hợp lệ hoặc đã được sử dụng"
            )

        # Kiểm tra token hết hạn
        if reset_token["expires_at"] < now:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token đã hết hạn"
            )

        user_id = reset_token["user_id"]

        # Kiểm tra tài khoản
        result = db.execute(
            text("""
                SELECT user_id, username
                FROM users
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        )

        user = result.mappings().first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy tài khoản"
            )

        # Cập nhật mật khẩu
        new_password_hash = hash_password(data.new_password)

        db.execute(
            text("""
                UPDATE users
                SET
                    password_hash = :password_hash,
                    updated_at = :updated_at
                WHERE user_id = :user_id
            """),
            {
                "password_hash": new_password_hash,
                "updated_at": now,
                "user_id": user_id
            }
        )

        # Đánh dấu token đã sử dụng
        db.execute(
            text("""
                UPDATE password_reset_tokens
                SET used_at = :used_at
                WHERE token = :token
            """),
            {
                "used_at": now,
                "token": data.token
            }
        )

        db.commit()

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise

    # Ghi audit đặt lại mật khẩu
    log_audit_event(
        db=db,
        user_id=user_id,
        action="RESET_PASSWORD",
        table_name="users",
        record_id=user_id,
        new_value={
            "username": user["username"]
        }
    )

    return {
        "message": "Đặt lại mật khẩu thành công"
    }


# =========================================================
# CHANGE PASSWORD
# =========================================================

@router.post("/change-password")
def change_password(
    data: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Đổi mật khẩu khi người dùng đã đăng nhập.

    Yêu cầu:
    - Có JWT hợp lệ
    - Nhập đúng mật khẩu hiện tại
    - Mật khẩu mới phải khác mật khẩu cũ
    """

    try:
        change_password_service(
            db=db,
            user=current_user,
            old_password=data.old_password,
            new_password=data.new_password
        )

        return {
            "message": "Đổi mật khẩu thành công"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
