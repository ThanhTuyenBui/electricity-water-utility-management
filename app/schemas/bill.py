from decimal import Decimal

from pydantic import BaseModel


class BillCalculationResponse(BaseModel):
    bill_id: int
    total_amount: Decimal
    message: str