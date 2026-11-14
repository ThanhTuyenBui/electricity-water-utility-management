
# Kết nối database.
# Lấy user đang đăng nhập từ JWT.
# Kiểm tra tài khoản có ACTIVE hay không.
# Kiểm tra quyền Admin, NhanVien, KhachHang.

import jwt

from types import SimpleNamespace

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import settings
from app.core.database import SessionLocal
from fastapi import Depends, HTTPException, status, Request

# ============================================================
# 1. XÁC THỰC JWT
# ============================================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


# ============================================================
# 2. KẾT NỐI DATABASE
# ============================================================

def get_db():
    """
    Tạo database session cho mỗi request.
    Sau khi request kết thúc thì đóng session.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ============================================================
# 3. LẤY THÔNG TIN USER ĐANG ĐĂNG NHẬP
# ============================================================



def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Giải mã JWT, kiểm tra tài khoản ACTIVE
    và thiết lập Audit Context cho request.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError, TypeError):
        raise credentials_exception

    # Truy vấn user và role
    query = text("""
        SELECT
            u.user_id,
            u.role_id,
            u.status,
            r.role_name
        FROM users u
        LEFT JOIN roles r
            ON u.role_id = r.role_id
        WHERE u.user_id = :user_id
    """)

    user = db.execute(
        query,
        {"user_id": user_id}
    ).mappings().first()

    if user is None:
        raise credentials_exception

    if user["status"] != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động"
        )

    # Lưu user_id vào SQLAlchemy Session
    db.info["audit_user_id"] = user["user_id"]

    # Thiết lập Audit Context trong transaction hiện tại
    db.execute(
        text("""
            SELECT set_config(
                'app.user_id',
                :user_id,
                true
            )
        """),
        {
            "user_id": str(user["user_id"])
        }
    )

    current_user = SimpleNamespace(
        user_id=user["user_id"],
        role_id=user["role_id"],
        status=user["status"],
        role_name=user["role_name"]
    )

    return current_user



# ============================================================
# 4. KIỂM TRA QUYỀN
# ============================================================

def require_roles(*allowed_roles):
    """
    Kiểm tra user có một trong các quyền được cho phép hay không.

    Ví dụ:

    require_roles("Admin")

    require_roles("Admin", "NhanVien")
    """

    def role_checker(
        current_user=Depends(get_current_user)
    ):

        # Kiểm tra role có tồn tại không
        if current_user.role_name is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không tìm thấy quyền của tài khoản"
            )

        # Kiểm tra quyền
        if current_user.role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện chức năng này"
            )

        return current_user

    return role_checker
