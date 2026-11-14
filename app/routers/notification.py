
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user, require_roles
from app.repositories import customer as customer_repository
from app.services import notification as notification_service

from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    NotificationRetryResponse,
    FailedNotificationListResponse
)


# =====================================================
# KHAI BÁO ROUTER
# =====================================================

# Router quản trị thông báo
router = APIRouter()

# Router thông báo dành cho khách hàng
customer_router = APIRouter()


# =====================================================
# I. API QUẢN TRỊ THÔNG BÁO
# =====================================================


# 1. LẤY DANH SÁCH THÔNG BÁO
# GET /api/notifications

@router.get(
    "",
    response_model=NotificationListResponse,
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def get_notifications_api(
    notification_status: str = Query(default=None, alias="status"),
    channel: str = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    try:
        return notification_service.get_notifications(
            db=db,
            status=notification_status,
            channel=channel,
            page=page,
            page_size=page_size
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# 2. LẤY DANH SÁCH THÔNG BÁO THẤT BẠI
# GET /api/notifications/failed

@router.get(
    "/failed",
    response_model=FailedNotificationListResponse,
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def get_failed_notifications_api(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    try:
        return notification_service.get_failed_notifications(
            db=db,
            page=page,
            page_size=page_size
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# 3. LẤY CHI TIẾT THÔNG BÁO
# GET /api/notifications/{notification_id}

@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def get_notification_by_id_api(
    notification_id: int,
    db: Session = Depends(get_db)
):
    try:
        return notification_service.get_notification_by_id(
            db=db,
            notification_id=notification_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# 4. GỬI LẠI THÔNG BÁO THẤT BẠI
# POST /api/notifications/{notification_id}/retry

@router.post(
    "/{notification_id}/retry",
    response_model=NotificationRetryResponse,
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def retry_notification_api(
    notification_id: int,
    db: Session = Depends(get_db)
):
    try:
        return notification_service.retry_notification(
            db=db,
            notification_id=notification_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        error_message = str(e)

        if "Không tìm thấy thông báo" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )

        if "Chỉ có thể gửi lại" in error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể gửi lại thông báo"
        )


# =====================================================
# II. API THÔNG BÁO DÀNH CHO KHÁCH HÀNG
# =====================================================


# 5. KHÁCH HÀNG LẤY DANH SÁCH THÔNG BÁO
# GET /api/customer/notifications

@customer_router.get(
    "/notifications",
    dependencies=[Depends(require_roles("KhachHang"))]
)
def get_customer_notifications_api(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        customer = customer_repository.get_my_customer(
            db=db,
            user_id=current_user.user_id
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )

        return notification_service.get_customer_notifications(
            db=db,
            customer_id=customer["customer_id"],
            limit=limit,
            offset=offset
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy danh sách thông báo"
        )


# 6. KHÁCH HÀNG ĐẾM SỐ THÔNG BÁO CHƯA ĐỌC
# GET /api/customer/notifications/unread-count

@customer_router.get(
    "/notifications/unread-count",
    dependencies=[Depends(require_roles("KhachHang"))]
)
def count_customer_unread_notifications_api(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        customer = customer_repository.get_my_customer(
            db=db,
            user_id=current_user.user_id
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )

        unread_count = notification_service.count_unread_notifications(
            db=db,
            customer_id=customer["customer_id"]
        )

        return {
            "unread_count": unread_count
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đếm thông báo chưa đọc"
        )


# 7. KHÁCH HÀNG XEM CHI TIẾT THÔNG BÁO
# GET /api/customer/notifications/{notification_id}

@customer_router.get(
    "/notifications/{notification_id}",
    dependencies=[Depends(require_roles("KhachHang"))]
)
def get_customer_notification_detail_api(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        customer = customer_repository.get_my_customer(
            db=db,
            user_id=current_user.user_id
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )

        return notification_service.get_customer_notification_detail(
            db=db,
            notification_id=notification_id,
            customer_id=customer["customer_id"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể lấy chi tiết thông báo"
        )


# 8. KHÁCH HÀNG ĐÁNH DẤU THÔNG BÁO ĐÃ ĐỌC
# PATCH /api/customer/notifications/{notification_id}/read

@customer_router.patch(
    "/notifications/{notification_id}/read",
    dependencies=[Depends(require_roles("KhachHang"))]
)
def mark_customer_notification_as_read_api(
    notification_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        customer = customer_repository.get_my_customer(
            db=db,
            user_id=current_user.user_id
        )

        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy thông tin khách hàng"
            )

        return notification_service.mark_notification_as_read(
            db=db,
            notification_id=notification_id,
            customer_id=customer["customer_id"]
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Không thể đánh dấu thông báo đã đọc"
        )
