from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query
)

from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    get_current_user,
    require_roles
)

from app.models.user import User

from app.schemas.meter import (
    MeterReadingCreate,
    MeterReadingResponse
)

from app.services.meter import (
    get_meters,
    get_meter_detail,
    get_meter_readings,
    get_meter_reading_detail,
    record_meter_reading
)


# ============================================================
# ROUTER QUẢN LÝ CÔNG TƠ
# ============================================================

router = APIRouter(
    prefix="/meters",
    tags=["Meters"]
)


# ============================================================
# 1. LẤY DANH SÁCH CÔNG TƠ
# Admin: tất cả
# Nhân viên: tất cả
# Khách hàng: công tơ của mình
# ============================================================

@router.get(
    "/",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien", "KhachHang"))
    ]
)
def api_get_meters(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_meters(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
        status=status
    )


# ============================================================
# 2. LẤY CHI TIẾT CÔNG TƠ
# ============================================================

@router.get(
    "/{meter_id}",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien", "KhachHang"))
    ]
)
def api_get_meter_detail(
    meter_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_meter_detail(
        db=db,
        current_user=current_user,
        meter_id=meter_id
    )


# ============================================================
# ROUTER QUẢN LÝ CHỈ SỐ CÔNG TƠ
# ============================================================

reading_router = APIRouter(
    prefix="/meter-readings",
    tags=["Meter Reading"]
)


# ============================================================
# 3. LẤY DANH SÁCH CHỈ SỐ CÔNG TƠ
# Admin: tất cả
# Nhân viên: tất cả
# Khách hàng: chỉ số của mình
# ============================================================

@reading_router.get(
    "/",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien", "KhachHang"))
    ]
)
def api_get_meter_readings(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    meter_id: int = None,
    reading_period: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_meter_readings(
        db=db,
        current_user=current_user,
        page=page,
        page_size=page_size,
        meter_id=meter_id,
        reading_period=reading_period
    )


# ============================================================
# 4. LẤY CHI TIẾT CHỈ SỐ CÔNG TƠ
# ============================================================

@reading_router.get(
    "/{reading_id}",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien", "KhachHang"))
    ]
)
def api_get_meter_reading_detail(
    reading_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_meter_reading_detail(
        db=db,
        current_user=current_user,
        reading_id=reading_id
    )


# ============================================================
# 5. GHI NHẬN CHỈ SỐ CÔNG TƠ
# Chỉ nhân viên được thực hiện
# ============================================================

@reading_router.post(
    "/",
    response_model=MeterReadingResponse,
    dependencies=[Depends(require_roles("NhanVien"))]
)
def api_record_meter_reading(
    data: MeterReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return record_meter_reading(
        db=db,
        current_user=current_user,
        data=data
    )