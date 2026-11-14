
from pydantic import BaseModel, Field


# ============================================================
# 1. ĐĂNG KÝ KHÁCH HÀNG
# ============================================================

class RegisterRequest(BaseModel):

    username: str = Field(
        min_length=4,
        max_length=50
    )

    email: str

    password: str = Field(
        min_length=6,
        max_length=100
    )

    full_name: str = Field(
        min_length=1,
        max_length=100
    )

    phone: str | None = None

    identity_number: str | None = None

    address: str | None = None

    # 1 = điện
    # 2 = nước
    # [1, 2] = cả điện và nước
    service_ids: list[int] = Field(
        min_length=1
    )


# ============================================================
# 2. TOKEN RESPONSE
# ============================================================

class TokenResponse(BaseModel):

    access_token: str
    token_type: str


# ============================================================
# 3. THÔNG TIN TÀI KHOẢN
# ============================================================

class UserResponse(BaseModel):

    user_id: int
    username: str
    role_id: int
    status: str
    email: str


# ============================================================
# 4. ĐẶT LẠI MẬT KHẨU
# ============================================================

class ResetPasswordRequest(BaseModel):

    token: str

    new_password: str = Field(
        min_length=6,
        max_length=100
    )


# ============================================================
# 5. ĐỔI MẬT KHẨU
# ============================================================

class ChangePasswordRequest(BaseModel):

    old_password: str = Field(
        min_length=6,
        max_length=100
    )

    new_password: str = Field(
        min_length=6,
        max_length=100
    )
