from pydantic import BaseModel, Field
from typing import Optional


class PaymentCreate(BaseModel):
    bill_id: int = Field(
        ...,
        gt=0,
        description="ID hóa đơn cần thanh toán"
    )

    transaction_code: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Mã giao dịch chuyển khoản"
    )