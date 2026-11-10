
from sqlalchemy.orm import Session

from app.repositories import notification as notification_repository


# =====================================================
# 1. LẤY DANH SÁCH THÔNG BÁO
# =====================================================

def get_notifications(
    db: Session,
    status: str = None,
    channel: str = None,
    page: int = 1,
    page_size: int = 20
):
    if status and status not in [
        "PENDING", "SENT", "SIMULATED", "FAILED", "READ"
    ]:
        raise ValueError("Trạng thái thông báo không hợp lệ")

    if channel and channel not in ["IN_APP", "SMS"]:
        raise ValueError("Kênh thông báo không hợp lệ")

    if page < 1 or page_size < 1:
        raise ValueError("Page và page_size phải lớn hơn 0")

    return notification_repository.get_notifications(
        db=db,
        status=status,
        channel=channel,
        page=page,
        page_size=page_size
    )


# =====================================================
# 2. LẤY CHI TIẾT THÔNG BÁO
# =====================================================

def get_notification_by_id(
    db: Session,
    notification_id: int
):
    if notification_id <= 0:
        raise ValueError("notification_id phải lớn hơn 0")

    notification = notification_repository.get_notification_by_id(
        db=db,
        notification_id=notification_id
    )

    if notification is None:
        raise ValueError("Không tìm thấy thông báo")

    return notification


# =====================================================
# 3. GỬI LẠI THÔNG BÁO THẤT BẠI
# =====================================================

def retry_notification(
    db: Session,
    notification_id: int
):
    if notification_id <= 0:
        raise ValueError("notification_id phải lớn hơn 0")

    try:
        result = notification_repository.retry_notification(
            db=db,
            notification_id=notification_id
        )

        db.commit()

        return {
            **result,
            "message": "Xử lý gửi lại thông báo thành công"
        }

    except Exception:
        db.rollback()
        raise


# =====================================================
# 4. LẤY DANH SÁCH THÔNG BÁO THẤT BẠI
# =====================================================

def get_failed_notifications(
    db: Session,
    page: int = 1,
    page_size: int = 20
):
    if page < 1 or page_size < 1:
        raise ValueError("Page và page_size phải lớn hơn 0")

    return notification_repository.get_failed_notifications(
        db=db,
        page=page,
        page_size=page_size
    )
 
# =====================================================
# 5. LẤY DANH SÁCH THÔNG BÁO CỦA KHÁCH HÀNG
# =====================================================

def get_customer_notifications(
    db: Session,
    customer_id: int,
    limit: int = 20,
    offset: int = 0
):
    if customer_id <= 0:
        raise ValueError("customer_id phải lớn hơn 0")

    if limit < 1 or limit > 100:
        raise ValueError("limit phải nằm trong khoảng từ 1 đến 100")

    if offset < 0:
        raise ValueError("offset không được nhỏ hơn 0")

    return notification_repository.get_customer_notifications(
        db=db,
        customer_id=customer_id,
        limit=limit,
        offset=offset
    )


# =====================================================
# 6. LẤY CHI TIẾT THÔNG BÁO CỦA KHÁCH HÀNG
# =====================================================

def get_customer_notification_detail(
    db: Session,
    notification_id: int,
    customer_id: int
):
    if notification_id <= 0 or customer_id <= 0:
        raise ValueError("Các ID phải lớn hơn 0")

    notification = notification_repository.get_customer_notification_detail(
        db=db,
        notification_id=notification_id,
        customer_id=customer_id
    )

    if notification is None:
        raise ValueError("Không tìm thấy thông báo")

    return notification


# =====================================================
# 7. ĐÁNH DẤU THÔNG BÁO ĐÃ ĐỌC
# =====================================================

def mark_notification_as_read(
    db: Session,
    notification_id: int,
    customer_id: int
):
    if notification_id <= 0 or customer_id <= 0:
        raise ValueError("Các ID phải lớn hơn 0")

    try:
        success = notification_repository.mark_notification_as_read(
            db=db,
            notification_id=notification_id,
            customer_id=customer_id
        )

        if not success:
            raise ValueError(
                "Không tìm thấy thông báo hoặc không thể đánh dấu đã đọc"
            )

        db.commit()

        return {
            "success": True,
            "message": "Đã đánh dấu thông báo là đã đọc"
        }

    except Exception:
        db.rollback()
        raise


# =====================================================
# 8. ĐẾM SỐ THÔNG BÁO CHƯA ĐỌC
# =====================================================

def count_unread_notifications(
    db: Session,
    customer_id: int
):
    if customer_id <= 0:
        raise ValueError("customer_id phải lớn hơn 0")

    return notification_repository.count_unread_notifications(
        db=db,
        customer_id=customer_id
    )
