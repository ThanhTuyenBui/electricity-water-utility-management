from pydantic import BaseModel, Field, EmailStr
from typing import Optional


# ============================================================
# 1. ĐĂNG KÝ KHÁCH HÀNG TẠI QUẦY
# ============================================================

class CounterRegisterRequest(BaseModel):

    username: str = Field(
        min_length=4,
        max_length=50
    )

    email: EmailStr

    full_name: str = Field(
        min_length=1,
        max_length=100
    )

    phone: Optional[str] = Field(
        default=None,
        pattern=r"^0[0-9]{9}$"
    )

    identity_number: Optional[str] = Field(
        default=None,
        max_length=20
    )

    address: Optional[str] = Field(
        default=None,
        max_length=255
    )

    # 1 = Điện
    # 2 = Nước
    # [1, 2] = cả hai
    service_ids: list[int] = Field(
        min_length=1
    )


# ============================================================
# 2. ĐĂNG KÝ THÊM DỊCH VỤ
# ============================================================

class AdditionalServiceRequest(BaseModel):

    service_id: int = Field(
        gt=0
    )

    installation_address: str = Field(
        min_length=1,
        max_length=255
    )


# ============================================================
# 3. RESPONSE CHO CÁC THAO TÁC DỊCH VỤ
# ============================================================

class CustomerServiceActionResponse(BaseModel):

    message: str

    user_id: int | None = None