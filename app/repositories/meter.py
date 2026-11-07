from sqlalchemy.orm import Session
from sqlalchemy import text


# ============================================================
# 1. LẤY ID KHÁCH HÀNG TỪ USER_ID
# ============================================================

def get_customer_id_by_user_id(db: Session, user_id: int):
    sql = text("""
        SELECT customer_id
        FROM customers
        WHERE user_id = :user_id
        LIMIT 1
    """)

    result = db.execute(sql, {"user_id": user_id}).mappings().first()

    return result["customer_id"] if result else None


# ============================================================
# 2. LẤY ID NHÂN VIÊN TỪ USER_ID
# ============================================================

def get_employee_id_by_user_id(db: Session, user_id: int):
    sql = text("""
        SELECT employee_id
        FROM employees
        WHERE user_id = :user_id
        LIMIT 1
    """)

    result = db.execute(sql, {"user_id": user_id}).mappings().first()

    return result["employee_id"] if result else None


# ============================================================
# 3. LẤY DANH SÁCH CÔNG TƠ
# ============================================================

def get_meters(
    db: Session,
    page: int,
    page_size: int,
    status: str = None,
    customer_id: int = None
):
    sql = text("""
        SELECT *
        FROM get_meters(
            :p_page,
            :p_page_size,
            :p_status,
            :p_customer_id
        )
    """)

    result = db.execute(sql, {
        "p_page": page,
        "p_page_size": page_size,
        "p_status": status,
        "p_customer_id": customer_id
    })

    return [dict(row) for row in result.mappings().all()]


# ============================================================
# 4. LẤY CHI TIẾT CÔNG TƠ
# ============================================================

def get_meter_detail(db: Session, meter_id: int):
    sql = text("""
        SELECT *
        FROM get_meter_detail(:p_meter_id)
    """)

    result = db.execute(sql, {
        "p_meter_id": meter_id
    })

    row = result.mappings().first()

    return dict(row) if row else None


# ============================================================
# 5. LẤY DANH SÁCH CHỈ SỐ CÔNG TƠ
# ============================================================

def get_meter_readings(
    db: Session,
    page: int,
    page_size: int,
    meter_id: int = None,
    reading_period: str = None,
    customer_id: int = None
):
    sql = text("""
        SELECT *
        FROM get_meter_readings(
            :p_page,
            :p_page_size,
            :p_meter_id,
            :p_reading_period,
            :p_customer_id
        )
    """)

    result = db.execute(sql, {
        "p_page": page,
        "p_page_size": page_size,
        "p_meter_id": meter_id,
        "p_reading_period": reading_period,
        "p_customer_id": customer_id
    })

    return [dict(row) for row in result.mappings().all()]


# ============================================================
# 6. LẤY CHI TIẾT CHỈ SỐ CÔNG TƠ
# ============================================================

def get_meter_reading_detail(db: Session, reading_id: int):
    sql = text("""
        SELECT *
        FROM get_meter_reading_detail(:p_reading_id)
    """)

    result = db.execute(sql, {
        "p_reading_id": reading_id
    })

    row = result.mappings().first()

    return dict(row) if row else None


# ============================================================
# 7. GHI NHẬN CHỈ SỐ CÔNG TƠ
# ============================================================


def record_meter_reading(
    db: Session,
    meter_id: int,
    reader_id: int,
    reading_period: str,
    current_reading,
    reading_date,
    image_url: str = None,
    abnormal_reason: str = None
):
    """
    Ghi nhận chỉ số công tơ và tự động xử lý hóa đơn
    thông qua PostgreSQL Function.
    
    Không commit tại Repository.
    """

    sql = text("""
        SELECT *
        FROM public.record_meter_reading_and_process_bill(
            :p_meter_id,
            :p_reader_id,
            :p_reading_period,
            :p_current_reading,
            :p_reading_date,
            :p_image_url,
            :p_abnormal_reason
        )
    """)

    try:
        result = db.execute(
            sql,
            {
                "p_meter_id": meter_id,
                "p_reader_id": reader_id,
                "p_reading_period": reading_period,
                "p_current_reading": current_reading,
                "p_reading_date": reading_date,
                "p_image_url": image_url,
                "p_abnormal_reason": abnormal_reason
            }
        )

        row = result.mappings().first()

        return dict(row) if row else None

    except Exception:
        db.rollback()
        raise


        

        return dict(row) if row else None

    except Exception:
        db.rollback()
        raise