
from sqlalchemy import text
from sqlalchemy.orm import Session


# =====================================================
# 1. LẤY DANH SÁCH THÔNG BÁO
# Hỗ trợ lọc trạng thái, kênh và phân trang
# =====================================================

def get_notifications(
    db: Session,
    status: str = None,
    channel: str = None,
    page: int = 1,
    page_size: int = 20
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_notifications(
                :p_status,
                :p_channel,
                :p_page,
                :p_page_size
            )
        """),
        {
            "p_status": status,
            "p_channel": channel,
            "p_page": page,
            "p_page_size": page_size
        }
    )

    rows = result.mappings().all()

    total_records = rows[0]["total_records"] if rows else 0

    return {
        "items": [dict(row) for row in rows],
        "total_records": total_records
    }


# =====================================================
# 2. LẤY CHI TIẾT THÔNG BÁO
# =====================================================

def get_notification_by_id(
    db: Session,
    notification_id: int
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_notification_by_id(
                :p_notification_id
            )
        """),
        {
            "p_notification_id": notification_id
        }
    )

    row = result.mappings().one_or_none()

    return dict(row) if row else None


# =====================================================
# 3. GỬI LẠI THÔNG BÁO THẤT BẠI
# =====================================================

def retry_notification(
    db: Session,
    notification_id: int
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.retry_notification(
                :p_notification_id
            )
        """),
        {
            "p_notification_id": notification_id
        }
    )

    row = result.mappings().one_or_none()

    return dict(row) if row else None


# =====================================================
# 4. LẤY DANH SÁCH THÔNG BÁO THẤT BẠI
# Hỗ trợ phân trang
# =====================================================

def get_failed_notifications(
    db: Session,
    page: int = 1,
    page_size: int = 20
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_failed_notifications(
                :p_page,
                :p_page_size
            )
        """),
        {
            "p_page": page,
            "p_page_size": page_size
        }
    )

    rows = result.mappings().all()

    total_records = rows[0]["total_records"] if rows else 0

    return {
        "items": [dict(row) for row in rows],
        "total_records": total_records
    }


# =====================================================
# 1. LẤY DANH SÁCH THÔNG BÁO CỦA KHÁCH HÀNG
# =====================================================

def get_customer_notifications(
    db: Session,
    customer_id: int,
    limit: int = 20,
    offset: int = 0
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_customer_notifications(
                :p_customer_id,
                :p_limit,
                :p_offset
            )
        """),
        {
            "p_customer_id": customer_id,
            "p_limit": limit,
            "p_offset": offset
        }
    )

    return [dict(row) for row in result.mappings().all()]


# =====================================================
# 2. LẤY CHI TIẾT THÔNG BÁO
# =====================================================

def get_customer_notification_detail(
    db: Session,
    notification_id: int,
    customer_id: int
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_customer_notification_detail(
                :p_notification_id,
                :p_customer_id
            )
        """),
        {
            "p_notification_id": notification_id,
            "p_customer_id": customer_id
        }
    )

    row = result.mappings().one_or_none()

    return dict(row) if row else None


# =====================================================
# 3. ĐÁNH DẤU THÔNG BÁO ĐÃ ĐỌC
# =====================================================

def mark_notification_as_read(
    db: Session,
    notification_id: int,
    customer_id: int
):
    result = db.execute(
        text("""
            SELECT public.mark_notification_as_read(
                :p_notification_id,
                :p_customer_id
            )
        """),
        {
            "p_notification_id": notification_id,
            "p_customer_id": customer_id
        }
    )

    return result.scalar()


# =====================================================
# 4. ĐẾM THÔNG BÁO CHƯA ĐỌC
# =====================================================

def count_unread_notifications(
    db: Session,
    customer_id: int
):
    result = db.execute(
        text("""
            SELECT public.count_unread_notifications(
                :p_customer_id
            )
        """),
        {
            "p_customer_id": customer_id
        }
    )

    return result.scalar()

