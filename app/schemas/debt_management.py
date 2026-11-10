
from pydantic import BaseModel, Field


class SuspendServiceRequest(BaseModel):
    customer_service_id: int = Field(
        ...,
        gt=0,
        description="ID đăng ký dịch vụ cần tạm ngừng"
    )

    current_reading: int = Field(
        ...,
        ge=0,
        description="Chỉ số công tơ tại thời điểm tạm ngừng"
    )


class RestoreServiceRequest(BaseModel):
    customer_service_id: int = Field(
        ...,
        gt=0,
        description="ID đăng ký dịch vụ cần khôi phục"
    )
