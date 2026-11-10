
from fastapi import HTTPException

from app.repositories import report as report_repository


def get_consumption_report(
    db,
    year: int = None,
    month: int = None,
    service_type: str = None
):
    if month is not None and not 1 <= month <= 12:
        raise HTTPException(
            status_code=400,
            detail="Tháng phải nằm trong khoảng từ 1 đến 12"
        )

    if month is not None and year is None:
        raise HTTPException(
            status_code=400,
            detail="Phải nhập năm khi nhập tháng"
        )

    if year is not None and year < 1:
        raise HTTPException(
            status_code=400,
            detail="Năm không hợp lệ"
        )

    if service_type is not None:
        service_type = service_type.upper()

        if service_type not in ["ELECTRICITY", "WATER"]:
            raise HTTPException(
                status_code=400,
                detail="Loại dịch vụ chỉ được là ELECTRICITY hoặc WATER"
            )

    return report_repository.get_consumption_report(
        db, year, month, service_type
    )


def get_revenue_report(
    db,
    year: int = None,
    month: int = None,
    service_type: str = None
):
    if month is not None and not 1 <= month <= 12:
        raise HTTPException(
            status_code=400,
            detail="Tháng phải nằm trong khoảng từ 1 đến 12"
        )

    if month is not None and year is None:
        raise HTTPException(
            status_code=400,
            detail="Phải nhập năm khi nhập tháng"
        )

    if year is not None and year < 1:
        raise HTTPException(
            status_code=400,
            detail="Năm không hợp lệ"
        )

    if service_type is not None:
        service_type = service_type.upper()

        if service_type not in ["ELECTRICITY", "WATER"]:
            raise HTTPException(
                status_code=400,
                detail="Loại dịch vụ chỉ được là ELECTRICITY hoặc WATER"
            )

    return report_repository.get_revenue_report(
        db, year, month, service_type
    )
