
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    get_current_user,
    require_roles
)

from app.models.user import User

from app.schemas.tariff import (
    TariffCreate,
    TariffVersionCreate,
    TariffUpdate
)

from app.services.tariff import (
    get_tariffs,
    get_tariff_detail,
    create_tariff,
    create_tariff_version,
    update_tariff
)


router = APIRouter(
    prefix="/tariffs",
    tags=["Tariff Management"]
)


# ============================================================
# 1. DANH SÁCH BIỂU GIÁ
# Admin: tất cả
# Nhân viên: tất cả
# Khách hàng: chỉ biểu giá ACTIVE
# ============================================================

@router.get(
    "/",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien", "KhachHang"))
    ]
)
def api_get_tariffs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = get_tariffs(
        db=db,
        role_id=current_user.role_id
    )

    return {
        "data": result
    }


# ============================================================
# 2. CHI TIẾT BIỂU GIÁ
# Admin: tất cả
# Nhân viên: tất cả
# Khách hàng: chỉ biểu giá ACTIVE
# ============================================================

@router.get(
    "/{tariff_id}",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien", "KhachHang"))
    ]
)
def api_get_tariff_detail(
    tariff_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = get_tariff_detail(
        db=db,
        tariff_id=tariff_id,
        role_id=current_user.role_id
    )

    return result


# ============================================================
# 3. ADMIN - TẠO BIỂU GIÁ
# ============================================================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_roles("Admin"))
    ]
)
def api_create_tariff(
    data: TariffCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_tariff(
            db=db,
            data=data.model_dump(mode="json")
        )

    except HTTPException:
        raise

    except Exception as e:
        print("Lỗi API tạo biểu giá:", repr(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi tạo biểu giá. Kiểm tra Terminal."
        )


# ============================================================
# 4. ADMIN - TẠO PHIÊN BẢN BIỂU GIÁ
# ============================================================

@router.post(
    "/{tariff_id}/versions",
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_roles("Admin"))
    ]
)
def api_create_tariff_version(
    tariff_id: int,
    data: TariffVersionCreate,
    db: Session = Depends(get_db)
):
    try:
        return create_tariff_version(
            db=db,
            tariff_id=tariff_id,
            data=data.model_dump(mode="json")
        )

    except HTTPException:
        raise

    except Exception as e:
        print("Lỗi API tạo phiên bản biểu giá:", repr(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi tạo phiên bản biểu giá. Kiểm tra Terminal."
        )


# ============================================================
# 5. ADMIN - CẬP NHẬT BIỂU GIÁ
# ============================================================

@router.put(
    "/{tariff_id}",
    dependencies=[
        Depends(require_roles("Admin"))
    ]
)
def api_update_tariff(
    tariff_id: int,
    data: TariffUpdate,
    db: Session = Depends(get_db)
):
    try:
        return update_tariff(
            db=db,
            tariff_id=tariff_id,
            data=data.model_dump(mode="json")
        )

    except HTTPException:
        raise

    except Exception as e:
        print("Lỗi API cập nhật biểu giá:", repr(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Đã xảy ra lỗi khi cập nhật biểu giá. Kiểm tra Terminal."
        )
