from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


# ============================================================
# ADMIN - TÌM KIẾM / PHÂN TRANG CÔNG TƠ
# ============================================================

class MeterSearchParams(BaseModel):
    search_area: str | None = None
    search_customer: str | None = None
    search_meter: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


# ============================================================
# ADMIN - CẬP NHẬT CÔNG TƠ
# ============================================================

class MeterUpdate(BaseModel):
    serial_number: str
    meter_type: str
    installation_date: date
    initial_reading: Decimal = Field(ge=0)
    status: str | None = None


# ============================================================
# RESPONSE - DANH SÁCH CÔNG TƠ
# ============================================================

class MeterListResponse(BaseModel):
    meter_name: str
    area: str | None
    customer_name: str


# ============================================================
# RESPONSE - CHI TIẾT CÔNG TƠ
# ============================================================

class MeterDetailResponse(BaseModel):
    meter_id: int
    serial_number: str
    meter_type: str
    installation_date: date
    initial_reading: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    customer_service_id: int
    customer_id: int
    service_id: int
    installation_address: str

    customer_name: str
    customer_phone: str | None
    customer_identity_number: str | None


# ============================================================
# RESPONSE - CÔNG TƠ CỦA KHÁCH HÀNG
# ============================================================

class MyMeterResponse(BaseModel):
    meter_id: int
    serial_number: str
    meter_type: str
    installation_date: date
    initial_reading: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    customer_service_id: int
    service_id: int
    service_name: str
    installation_address: str