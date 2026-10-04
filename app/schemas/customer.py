from pydantic import BaseModel, Field, EmailStr
from typing import Optional


# =========================================================
# 1. KHÁCH HÀNG TỰ SỬA THÔNG TIN
# =========================================================

class CustomerSelfUpdate(BaseModel):

    full_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    email: Optional[EmailStr] = None

    phone: Optional[str] = Field(
        default=None,
        max_length=15
    )

    identity_number: Optional[str] = Field(
        default=None,
        max_length=20
    )


# =========================================================
# 2. RESPONSE THÔNG TIN KHÁCH HÀNG
# =========================================================

class CustomerResponse(BaseModel):

    customer_id: int
    user_id: int
    full_name: str
    phone: Optional[str]
    identity_number: Optional[str]
    address: Optional[str]
    status: str

    class Config:
        from_attributes = True


# =========================================================
# 3. CẬP NHẬT TRẠNG THÁI KHÁCH HÀNG
# =========================================================

class CustomerStatusUpdate(BaseModel):

    status: str