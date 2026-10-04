from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    get_current_user,
    require_roles
)

from app.models.user import User

from app.schemas.meter import (
    MeterUpdate
)

from app.services.meter import (
    get_meters_for_admin_service,
    get_meter_detail_service,
    update_meter_after_approval_service,
    get_my_meters_service
)


router = APIRouter(
    prefix="/meters",
    tags=["Meters"]
)


# ============================================================
# 1. ADMIN - DANH SÁCH / TÌM KIẾM CÔNG TƠ
# ============================================================

@router.get(
    "/",
    dependencies=[
        Depends(require_roles("Admin"))
    ]
)
def get_meters_for_admin(
    search_area: str | None = Query(default=None),
    search_customer: str | None = Query(default=None),
    search_meter: str | None = Query(default=None),

    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),

    db: Session = Depends(get_db)
):
    try:

        result = get_meters_for_admin_service(
            db=db,
            search_area=search_area,
            search_customer=search_customer,
            search_meter=search_meter,
            page=page,
            page_size=page_size
        )

        return {
            "page": page,
            "page_size": page_size,
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================
# 2. ADMIN - XEM CHI TIẾT CÔNG TƠ
# ============================================================

@router.get(
    "/{meter_id}",
    dependencies=[
        Depends(require_roles("Admin"))
    ]
)
def get_meter_detail(
    meter_id: int,
    db: Session = Depends(get_db)
):
    try:

        result = get_meter_detail_service(
            db=db,
            meter_id=meter_id
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ============================================================
# 3. ADMIN - CẬP NHẬT CÔNG TƠ SAU KHI DUYỆT ĐƠN
# ============================================================

@router.put(
    "/{meter_id}",
    dependencies=[
        Depends(require_roles("Admin"))
    ]
)
def update_meter(
    meter_id: int,
    data: MeterUpdate,
    db: Session = Depends(get_db)
):
    try:

        update_meter_after_approval_service(
            db=db,
            meter_id=meter_id,
            serial_number=data.serial_number,
            meter_type=data.meter_type,
            installation_date=data.installation_date,
            initial_reading=data.initial_reading,
            status=data.status
        )

        return {
            "message": "Cập nhật công tơ thành công"
        }

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================
# 4. KHÁCH HÀNG - XEM CÔNG TƠ CỦA MÌNH
# ============================================================

@router.get(
    "/my/list",
    dependencies=[
        Depends(require_roles("KhachHang"))
    ]
)
def get_my_meters(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:

        # Lấy customer_id từ user đăng nhập
        customer_id = current_user.customer_id

        result = get_my_meters_service(
            db=db,
            customer_id=customer_id
        )

        return {
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )