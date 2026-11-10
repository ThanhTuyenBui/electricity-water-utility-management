from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    Request
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
    MeterInstallRequest
)

from app.services.meter import (
    get_meters,
    get_meter_detail,
    get_meter_readings,
    get_meter_reading_detail,
    record_meter_reading,
    install_meter
)


# ============================================================
# ROUTER QUẢN LÝ CÔNG TƠ
# ============================================================

router = APIRouter(
    prefix="/meters",
    tags=["Meters"]
)

# ============================================================
# 1. CẬP NHẬT THÔNG TIN LẮP ĐẶT CÔNG TƠ
# Chỉ Admin và Nhân viên được thực hiện
# ============================================================

@router.put(
    "/{meter_id}/install",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien"))
    ]
)
def api_install_meter(
    meter_id: int,
    data: MeterInstallRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return install_meter(
        db=db,
        current_user=current_user,
        meter_id=meter_id,
        data=data
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
    tags=["Meter Readings"]
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


# ============================================================
# 5. GHI NHẬN CHỈ SỐ CÔNG TƠ
# Chỉ nhân viên được thực hiện
# ============================================================

@reading_router.post(
    "/",
    dependencies=[Depends(require_roles("NhanVien"))]
)
def api_record_meter_reading(
    data: MeterReadingCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = record_meter_reading(
        db=db,
        current_user=current_user,
        data=data,
        ip_address=request.client.host if request.client else None
    )

    return {
        "message": "Ghi nhận chỉ số thành công"
    }
