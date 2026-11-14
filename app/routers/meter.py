from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Query,
    Request,
    UploadFile, File, Form
)
from datetime import date
from decimal import Decimal

from app.providers.storage.image_storage import (
    save_meter_reading_image,
    delete_meter_reading_image
)

from sqlalchemy.orm import Session
 
from app.core.dependencies import (
    get_db,
    get_current_user,
    require_roles
)



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
    current_user = Depends(get_current_user)
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
    current_user = Depends(get_current_user)
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
    current_user = Depends(get_current_user)
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
    current_user = Depends(get_current_user)
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
    current_user = Depends(get_current_user)
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

async def api_record_meter_reading(
    meter_id: int = Form(..., gt=0),
    reading_period: str = Form(..., min_length=7, max_length=7),
    current_reading: Decimal = Form(..., ge=0),
    reading_date: date = Form(...),
    image: UploadFile = File(...),
    abnormal_reason: str = Form(None),

    request: Request = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    image_url = None

    try:
        # 1. Kiểm tra định dạng ảnh
        allowed_types = [
            "image/jpeg",
            "image/png",
            "image/webp"
        ]

        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Chỉ chấp nhận ảnh JPG, PNG hoặc WEBP"
            )

        # 2. Đọc ảnh và kiểm tra dung lượng (tối đa 5MB)
        image_data = await image.read(5 * 1024 * 1024 + 1)

        if not image_data:
            raise HTTPException(
                status_code=400,
                detail="Ảnh công tơ không được để trống"
            )

        if len(image_data) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="Dung lượng ảnh tối đa là 5MB"
            )

        # 3. Kiểm tra chữ ký file thực tế
        valid_signatures = {
            "image/jpeg": lambda b: b.startswith(b"\xff\xd8\xff"),
            "image/png": lambda b: b.startswith(b"\x89PNG\r\n\x1a\n"),
            "image/webp": lambda b: (
                len(b) >= 12
                and b.startswith(b"RIFF")
                and b[8:12] == b"WEBP"
            )
        }

        if not valid_signatures[image.content_type](image_data):
            raise HTTPException(
                status_code=400,
                detail="Nội dung file không phải ảnh hợp lệ"
            )

        # 4. Lưu ảnh vào máy chủ
        image_url = save_meter_reading_image(
            image_data=image_data,
            content_type=image.content_type
        )

        # 5. Gọi service ghi nhận chỉ số
        result = record_meter_reading(
            db=db,
            current_user=current_user,
            meter_id=meter_id,
            reading_period=reading_period,
            current_reading=current_reading,
            reading_date=reading_date,
            image_url=image_url,
            abnormal_reason=abnormal_reason,
            ip_address=request.client.host if request.client else None
        )

        return result

    except Exception:
        # Nếu ghi DB thất bại thì xóa ảnh vừa upload
        if image_url:
            delete_meter_reading_image(image_url)

        raise

    finally:
        await image.close()

