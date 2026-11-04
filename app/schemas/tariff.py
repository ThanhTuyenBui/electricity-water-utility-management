from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# 1. THÔNG TIN BẬC GIÁ
# ============================================================

class TariffTierCreate(BaseModel):

    from_value: Decimal = Field(
        ge=0,
        description="Sản lượng bắt đầu của bậc giá"
    )

    to_value: Optional[Decimal] = Field(
        default=None,
        ge=0,
        description="Sản lượng kết thúc; null là không giới hạn"
    )

    unit_price: Decimal = Field(
        ge=0,
        description="Đơn giá"
    )


# ============================================================
# 2. TẠO BIỂU GIÁ
# ============================================================

class TariffCreate(BaseModel):

    service_id: int = Field(
        gt=0
    )

    effective_from: date

    vat_percent: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100
    )

    environment_fee_percent: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100
    )

    tiers: list[TariffTierCreate] = Field(
        min_length=1
    )


# ============================================================
# 3. TẠO PHIÊN BẢN BIỂU GIÁ
# ============================================================

class TariffVersionCreate(BaseModel):

    effective_from: date

    vat_percent: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100
    )

    environment_fee_percent: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100
    )

    # Nếu không truyền tiers hoặc truyền null:
    # Sử dụng lại các bậc giá của biểu giá nguồn.

    tiers: Optional[list[TariffTierCreate]] = None


# ============================================================
# 4. CẬP NHẬT BIỂU GIÁ
# ============================================================

class TariffUpdate(BaseModel):

    # Theo PostgreSQL Function hiện tại,
    # tiers là tham số bắt buộc.

    tiers: list[TariffTierCreate] = Field(
        min_length=1
    )

    vat_percent: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100
    )

    environment_fee_percent: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100
    )


# ============================================================
# 5. RESPONSE DANH SÁCH BIỂU GIÁ
# ============================================================

class TariffResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    tariff_id: int
    service_id: int
    service_name: str

    effective_from: date
    effective_to: Optional[date] = None

    created_at: datetime

    vat_percent: Optional[Decimal] = None
    environment_fee_percent: Optional[Decimal] = None

    tariff_status: str


# ============================================================
# 6. RESPONSE CHI TIẾT BIỂU GIÁ
# ============================================================

class TariffDetailResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    tariff_id: int
    service_id: int
    service_name: str

    effective_from: date
    effective_to: Optional[date] = None

    created_at: datetime

    vat_percent: Optional[Decimal] = None
    environment_fee_percent: Optional[Decimal] = None

    tier_id: int
    from_value: Decimal
    to_value: Optional[Decimal] = None
    unit_price: Decimal


# ============================================================
# 7. RESPONSE CHO CÁC THAO TÁC
# ============================================================

class TariffActionResponse(BaseModel):

    message: str
    tariff_id: Optional[int] = None