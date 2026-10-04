from sqlalchemy import text
from sqlalchemy.orm import Session


# ============================================================
# 1. ADMIN - LẤY DANH SÁCH CÔNG TƠ
# ============================================================

def get_meters_for_admin(
    db: Session,
    search_area: str | None,
    search_customer: str | None,
    search_meter: str | None,
    page: int,
    page_size: int
):
    cursor_name = "meter_admin_cursor"

    db.execute(
        text(
            """
            CALL get_meters_for_admin(
                :p_search_area,
                :p_search_customer,
                :p_search_meter,
                :p_page,
                :p_page_size,
                :p_result
            )
            """
        ),
        {
            "p_search_area": search_area,
            "p_search_customer": search_customer,
            "p_search_meter": search_meter,
            "p_page": page,
            "p_page_size": page_size,
            "p_result": cursor_name
        }
    )

    result = db.execute(
        text(f'FETCH ALL FROM "{cursor_name}"')
    )

    return result.mappings().all()


# ============================================================
# 2. ADMIN - XEM CHI TIẾT CÔNG TƠ
# ============================================================

def get_meter_detail(
    db: Session,
    meter_id: int
):
    cursor_name = "meter_detail_cursor"

    db.execute(
        text(
            """
            CALL get_meter_detail(
                :p_meter_id,
                :p_result
            )
            """
        ),
        {
            "p_meter_id": meter_id,
            "p_result": cursor_name
        }
    )

    result = db.execute(
        text(f'FETCH ALL FROM "{cursor_name}"')
    )

    return result.mappings().first()


# ============================================================
# 3. ADMIN / NHÂN VIÊN - CẬP NHẬT CÔNG TƠ
# ============================================================

def update_meter_after_approval(
    db: Session,
    meter_id: int,
    serial_number: str,
    meter_type: str,
    installation_date,
    initial_reading,
    status: str | None
):
    db.execute(
        text(
            """
            CALL update_meter_after_approval(
                :p_meter_id,
                :p_serial_number,
                :p_meter_type,
                :p_installation_date,
                :p_initial_reading,
                :p_status
            )
            """
        ),
        {
            "p_meter_id": meter_id,
            "p_serial_number": serial_number,
            "p_meter_type": meter_type,
            "p_installation_date": installation_date,
            "p_initial_reading": initial_reading,
            "p_status": status
        }
    )


# ============================================================
# 4. KHÁCH HÀNG - XEM CÔNG TƠ CỦA MÌNH
# ============================================================

def get_my_meters(
    db: Session,
    customer_id: int
):
    cursor_name = "my_meter_cursor"

    db.execute(
        text(
            """
            CALL get_my_meters(
                :p_customer_id,
                :p_result
            )
            """
        ),
        {
            "p_customer_id": customer_id,
            "p_result": cursor_name
        }
    )

    result = db.execute(
        text(f'FETCH ALL FROM "{cursor_name}"')
    )

    return result.mappings().all()