from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_roles
from app.services import debt_management as debt_management_service
from app.schemas.debt_management import (
    SuspendServiceRequest,
    RestoreServiceRequest
)
from app.core.dependencies import get_current_user
router = APIRouter()


# 1. Tra cứu công nợ khách hàng
@router.get(
    "/summary",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien"))
    ]
)
def get_customer_debt_summary_api(
    customer_id: int | None = Query(
        default=None,
        gt=0
    ),
    db: Session = Depends(get_db)
):
    try:
        return debt_management_service.get_customer_debt_summary_service(
            db=db,
            customer_id=customer_id
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Lỗi khi thống kê công nợ khách hàng"
        )


# 2. Danh sách công nợ tất cả khách hàng có phân trang
@router.get(
    "/list",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien"))
    ]
)
def get_customer_debt_list_api(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    try:
        return debt_management_service.get_customer_debt_list_service(
            db=db,
            page=page,
            page_size=page_size
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Lỗi khi lấy danh sách công nợ"
        )


# 3. Danh sách khách hàng đang có nợ
@router.get(
    "/debtors",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien"))
    ]
)
def get_customers_with_debt_api(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    try:
        return debt_management_service.get_customers_with_debt_service(
            db=db,
            page=page,
            page_size=page_size
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Lỗi khi lấy danh sách khách hàng đang có nợ"
        )


    
# =====================================================
# TẠM NGỪNG DỊCH VỤ DO NỢ
# =====================================================

@router.get(
    "/suspension/eligible",
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def get_services_eligible_for_suspension(
    db: Session = Depends(get_db)
):
    try:
        return debt_management_service.get_services_eligible_for_debt_suspension_service(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post(
    "/suspension/confirm",
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def suspend_service_for_debt(
    data: SuspendServiceRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        debt_management_service.suspend_customer_service_for_debt_service(
            db=db,
            customer_service_id=data.customer_service_id,
            user_id=current_user.user_id,
            current_reading=data.current_reading
        )

        return {
            "message": "Tạm ngừng dịch vụ do nợ thành công."
        }

    except ValueError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau."
        )
# =====================================================
# KHÔI PHỤC DỊCH VỤ SAU KHI THANH TOÁN NỢ
# =====================================================

@router.get(
    "/restoration/eligible",
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def get_services_eligible_for_restoration(
    db: Session = Depends(get_db)
):
    try:
        return debt_management_service.get_services_eligible_for_debt_restoration_service(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/restoration/confirm",
    dependencies=[Depends(require_roles("Admin", "NhanVien"))]
)
def restore_service_after_debt_payment(
    data: RestoreServiceRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        debt_management_service.restore_customer_service_after_debt_payment_service(
            db=db,
            customer_service_id=data.customer_service_id,
            user_id=current_user.user_id
        )

        return {
            "message": "Khôi phục dịch vụ thành công."
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))