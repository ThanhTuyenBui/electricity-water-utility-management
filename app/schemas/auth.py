from pydantic import BaseModel, Field


# Dữ liệu khách hàng gửi khi đăng ký
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


#TokenResponse là kết quả sau khi đăng nhập thành công:
class TokenResponse(BaseModel):
    access_token: str
    token_type: str

#UserResponse dùng để trả thông tin tài khoản mà không trả password_hash
class UserResponse(BaseModel):
    user_id: int
    username: str
    role_id: int
    status: str
    email: str
    class Config:
        from_attributes = True
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(
        min_length=6,
        max_length=100
    )        