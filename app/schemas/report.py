
from pydantic import BaseModel
from typing import List


class ConsumptionReportResponse(BaseModel):
    report_period: str
    service_type: str
    service_name: str
    unit: str
    total_consumption: float
    total_bills: int


class RevenueReportResponse(BaseModel):
    report_period: str
    service_type: str
    service_name: str
    total_revenue: float
    total_bills: int
