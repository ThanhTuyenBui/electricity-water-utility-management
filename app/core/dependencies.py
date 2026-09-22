# Kết nối database.
# Lấy user đang đăng nhập từ JWT.
# Kiểm tra tài khoản có ACTIVE hay không.
# Kiểm tra quyền Admin, NhanVien, KhachHang.
import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.database import SessionLocal
from app.models.user import User
from app.models.role import Role


# FastAPI sẽ lấy JWT từ:
# Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


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


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Lấy thông tin user từ JWT token.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token không hợp lệ hoặc đã hết hạn",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        # Giải mã JWT
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Lấy user_id từ trường sub
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = int(user_id)

    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception

    # Tìm user trong database
    user = (
        db.query(User)
        .filter(User.user_id == user_id)
        .first()
    )

    if user is None:
        raise credentials_exception

    # Chỉ tài khoản ACTIVE mới được sử dụng hệ thống
    if user.status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tài khoản không hoạt động"
        )

    return user


def require_roles(*allowed_roles):
    """
    Kiểm tra user có một trong các quyền được cho phép hay không.

    Ví dụ:

    require_roles("Admin")

    hoặc:

    require_roles("Admin", "NhanVien")
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        # Tìm role của user
        role = (
            db.query(Role)
            .filter(Role.role_id == current_user.role_id)
            .first()
        )

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không tìm thấy quyền của tài khoản"
            )

        # Kiểm tra role
        if role.role_name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Bạn không có quyền thực hiện chức năng này"
            )

        return current_user

    return role_checker