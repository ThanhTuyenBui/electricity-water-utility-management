from pydantic import BaseModel, Field
from datetime import date
from decimal import Decimal
from typing import Optional


# ============================================================
# SCHEMA: GHI NHẬN CHỈ SỐ CÔNG TƠ
# ============================================================

class MeterReadingCreate(BaseModel):

    meter_id: int = Field(
        ...,
        gt=0,
        description="ID công tơ"
    )

    reading_period: str = Field(
        ...,
        min_length=7,
        max_length=7,
        description="Kỳ ghi nhận theo định dạng YYYY-MM"
    )

    current_reading: Decimal = Field(
        ...,
        ge=0,
        description="Chỉ số hiện tại"
    )

    reading_date: date = Field(
        ...,
        description="Ngày ghi nhận"
    )

    image_url: Optional[str] = Field(
        default=None,
        description="Đường dẫn ảnh công tơ"
    )

    abnormal_reason: Optional[str] = Field(
        default=None,
        description="Lý do nếu chỉ số bất thường"
    )


#cấp nhật sau khi lắp
class MeterInstallRequest(BaseModel):
    serial_number: str = Field(
        ...,
        min_length=1,
        description="Số seri công tơ"
    )

    meter_type: str = Field(
        ...,
        min_length=1,
        description="Loại công tơ"
    )

    installation_date: date

    initial_reading: int = Field(
        ...,
        ge=0,
        description="Chỉ số ban đầu của công tơ"
    )

class MeterReadingResponse(BaseModel):
    message: str

    data: dict
