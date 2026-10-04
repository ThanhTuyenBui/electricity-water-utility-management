from sqlalchemy.orm import Session

from app.repositories.meter import (
    get_meters_for_admin as get_meters_for_admin_repo,
    get_meter_detail as get_meter_detail_repo,
    update_meter_after_approval as update_meter_after_approval_repo,
    get_my_meters as get_my_meters_repo
)


# ============================================================
# 1. ADMIN - LẤY DANH SÁCH CÔNG TƠ
# ============================================================

def get_meters_for_admin_service(
    db: Session,
    search_area: str | None,
    search_customer: str | None,
    search_meter: str | None,
    page: int,
    page_size: int
):
    try:
        return get_meters_for_admin_repo(
            db=db,
            search_area=search_area,
            search_customer=search_customer,
            search_meter=search_meter,
            page=page,
            page_size=page_size
        )

    except Exception:
        raise


# ============================================================
# 2. ADMIN - CHI TIẾT CÔNG TƠ
# ============================================================

def get_meter_detail_service(
    db: Session,
    meter_id: int
):
    try:
        result = get_meter_detail_repo(
            db=db,
            meter_id=meter_id
        )

        if result is None:
            raise ValueError("Không tìm thấy công tơ")

        return result

    except Exception:
        raise


# ============================================================
# 3. ADMIN / NHÂN VIÊN - CẬP NHẬT CÔNG TƠ
# ============================================================

def update_meter_after_approval_service(
    db: Session,
    meter_id: int,
    serial_number: str,
    meter_type: str,
    installation_date,
    initial_reading,
    status: str | None
):
    try:
        update_meter_after_approval_repo(
            db=db,
            meter_id=meter_id,
            serial_number=serial_number,
            meter_type=meter_type,
            installation_date=installation_date,
            initial_reading=initial_reading,
            status=status
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


# ============================================================
# 4. KHÁCH HÀNG - XEM CÔNG TƠ CỦA MÌNH
# ============================================================

def get_my_meters_service(
    db: Session,
    customer_id: int
):
    try:
        return get_my_meters_repo(
            db=db,
            customer_id=customer_id
        )

    except Exception:
        raise