from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.repositories import meter as meter_repo


# ============================================================
# XỬ LÝ LỖI DATABASE
# ============================================================

def handle_meter_database_error(db, exc):

    db.rollback()

    original_error = getattr(exc, "orig", None)
    error_code = getattr(original_error, "pgcode", None)

    if error_code == "23505":
        raise HTTPException(
            status_code=409,
            detail="Dữ liệu đã tồn tại"
        )

    if error_code == "P0001":
        message = str(original_error).splitlines()[0]
        message = message.replace("ERROR:", "").strip()

        raise HTTPException(
            status_code=400,
            detail=message
        )

    raise HTTPException(
        status_code=500,
        detail="Lỗi xử lý dữ liệu trong cơ sở dữ liệu"
    )


# ============================================================
# 1. LẤY DANH SÁCH CÔNG TƠ
# ============================================================

def get_meters(
    db,
    current_user,
    page: int,
    page_size: int,
    status: str = None
):
    try:
        customer_id = None

        # Khách hàng chỉ được xem công tơ của mình
        if current_user.role_id == 3:

            customer_id = meter_repo.get_customer_id_by_user_id(
                db,
                current_user.user_id
            )

            if customer_id is None:
                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy thông tin khách hàng"
                )

        rows = meter_repo.get_meters(
            db=db,
            page=page,
            page_size=page_size,
            status=status,
            customer_id=customer_id
        )

        total = rows[0]["total_count"] if rows else 0

        return {
            "items": rows,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    except HTTPException:
        raise

    except SQLAlchemyError as exc:
        handle_meter_database_error(db, exc)


# ============================================================
# 2. LẤY CHI TIẾT CÔNG TƠ
# ============================================================

def get_meter_detail(
    db,
    current_user,
    meter_id: int
):
    try:
        result = meter_repo.get_meter_detail(
            db,
            meter_id
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy công tơ"
            )

        # Kiểm tra quyền sở hữu đối với khách hàng
        if current_user.role_id == 3:

            customer_id = meter_repo.get_customer_id_by_user_id(
                db,
                current_user.user_id
            )

            if customer_id is None or result["customer_id"] != customer_id:
                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy công tơ"
                )

        return result

    except HTTPException:
        raise

    except SQLAlchemyError as exc:
        handle_meter_database_error(db, exc)


# ============================================================
# 3. LẤY DANH SÁCH CHỈ SỐ CÔNG TƠ
# ============================================================

def get_meter_readings(
    db,
    current_user,
    page: int,
    page_size: int,
    meter_id: int = None,
    reading_period: str = None
):
    try:
        customer_id = None

        # Khách hàng chỉ xem chỉ số của mình
        if current_user.role_id == 3:

            customer_id = meter_repo.get_customer_id_by_user_id(
                db,
                current_user.user_id
            )

            if customer_id is None:
                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy thông tin khách hàng"
                )

        rows = meter_repo.get_meter_readings(
            db=db,
            page=page,
            page_size=page_size,
            meter_id=meter_id,
            reading_period=reading_period,
            customer_id=customer_id
        )

        total = rows[0]["total_count"] if rows else 0

        return {
            "items": rows,
            "total": total,
            "page": page,
            "page_size": page_size
        }

    except HTTPException:
        raise

    except SQLAlchemyError as exc:
        handle_meter_database_error(db, exc)


# ============================================================
# 4. LẤY CHI TIẾT CHỈ SỐ CÔNG TƠ
# ============================================================

def get_meter_reading_detail(
    db,
    current_user,
    reading_id: int
):
    try:
        result = meter_repo.get_meter_reading_detail(
            db,
            reading_id
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy bản ghi chỉ số"
            )

        # Khách hàng chỉ xem chỉ số của mình
        if current_user.role_id == 3:

            customer_id = meter_repo.get_customer_id_by_user_id(
                db,
                current_user.user_id
            )

            if customer_id is None or result["customer_id"] != customer_id:
                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy bản ghi chỉ số"
                )

        return result

    except HTTPException:
        raise

    except SQLAlchemyError as exc:
        handle_meter_database_error(db, exc)


# ============================================================
# 5. GHI NHẬN CHỈ SỐ CÔNG TƠ
# ============================================================


def record_meter_reading(
    db,
    current_user,
    data
):
    try:
        # 1. Xác định nhân viên đang đăng nhập
        reader_id = meter_repo.get_employee_id_by_user_id(
            db,
            current_user.user_id
        )

        if reader_id is None:
            raise HTTPException(
                status_code=403,
                detail="Tài khoản không có thông tin nhân viên"
            )

        # 2. Ghi chỉ số và tự động xử lý hóa đơn
        result = meter_repo.record_meter_reading(
            db=db,
            meter_id=data.meter_id,
            reader_id=reader_id,
            reading_period=data.reading_period,
            current_reading=data.current_reading,
            reading_date=data.reading_date,
            image_url=data.image_url,
            abnormal_reason=data.abnormal_reason
        )

        if not result:
            raise HTTPException(
                status_code=400,
                detail="Không thể ghi nhận chỉ số công tơ"
            )

        # 3. Xác định thông báo theo trạng thái hóa đơn
        if result["readings_complete"]:
            message = (
                "Ghi nhận chỉ số thành công và "
                "đã tự động tính tiền hóa đơn"
            )
        else:
            message = (
                "Ghi nhận chỉ số thành công. "
                "Hóa đơn đang chờ ghi nhận chỉ số "
                "các công tơ còn lại"
            )

        # 4. Commit transaction
        db.commit()

        return {
            "message": message,
            "data": result
        }

    except HTTPException:
        db.rollback()
        raise

    except SQLAlchemyError as exc:
        handle_meter_database_error(db, exc)

    except Exception:
        db.rollback()
        raise
