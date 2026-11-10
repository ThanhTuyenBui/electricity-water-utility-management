
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.dependencies import get_db, require_roles
from app.services import report as report_service
from app.schemas.report import (
    ConsumptionReportResponse,
    RevenueReportResponse
)

router = APIRouter()


# 1. API báo cáo sản lượng tiêu thụ
@router.get(
    "/consumption",
    response_model=List[ConsumptionReportResponse],
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def get_consumption_report(
    year: int = None,
    month: int = None,
    service_type: str = None,
    db: Session = Depends(get_db),
    
):
    return report_service.get_consumption_report(
        db, year, month, service_type
    )


# 2. API báo cáo doanh thu
@router.get(
    "/revenue",
    response_model=List[RevenueReportResponse],
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def get_revenue_report(
    year: int = None,
    month: int = None,
    service_type: str = None,
    db: Session = Depends(get_db),
   
):
    return report_service.get_revenue_report(
        db, year, month, service_type
    )
