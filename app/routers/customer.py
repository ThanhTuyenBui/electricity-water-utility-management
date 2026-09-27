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
    require_roles
)

from app.models.user import User

from app.schemas.customer import (
    CustomerSelfUpdate,
    CustomerStatusUpdate
)

from app.services.customer import (
    get_my_customer_service,
    update_customer_self_service,
    get_customers_service,
    change_customer_status_service
)


router = APIRouter()


# =========================================================
# 1. KHÁCH HÀNG XEM THÔNG TIN CỦA CHÍNH MÌNH
# =========================================================

@router.get("/me")
def get_my_customer(

    current_user: User = Depends(
        require_roles("KhachHang")
    ),

    db: Session = Depends(get_db)
):

    result = get_my_customer_service(
        db=db,
        user_id=current_user.user_id
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin khách hàng"
        )

    return result


# =========================================================
# 2. KHÁCH HÀNG SỬA THÔNG TIN CỦA CHÍNH MÌNH
# =========================================================

@router.put("/me")
def update_my_customer(

    data: CustomerSelfUpdate,

    current_user: User = Depends(
        require_roles("KhachHang")
    ),

    db: Session = Depends(get_db)
):

    update_data = data.model_dump(
        exclude_unset=True
    )

    if not update_data:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Không có thông tin cần cập nhật"
        )

    try:

        update_customer_self_service(
            db=db,

            user_id=current_user.user_id,

            full_name=update_data.get(
                "full_name"
            ),

            phone=update_data.get(
                "phone"
            ),

            identity_number=update_data.get(
                "identity_number"
            )
        )

        return {
            "message":
                "Cập nhật thông tin khách hàng thành công"
        }

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =========================================================
# 3. ADMIN / NHÂN VIÊN XEM DANH SÁCH KHÁCH HÀNG
# =========================================================

@router.get("/")
def get_customers(

    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        10,
        ge=1,
        le=100
    ),

    search: str | None = Query(
        default=None
    ),

    area: str | None = Query(
        default=None
    ),

    sort_by: str = Query(
        default="customer_id"
    ),

    sort_order: str = Query(
        default="ASC"
    ),

    current_user: User = Depends(
        require_roles(
            "Admin",
            "NhanVien"
        )
    ),

    db: Session = Depends(get_db)
):

    if sort_order.upper() not in (
        "ASC",
        "DESC"
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="sort_order chỉ được ASC hoặc DESC"
        )

    allowed_sort_fields = {
        "customer_id",
        "full_name",
        "phone",
        "identity_number",
        "address",
        "status"
    }

    if sort_by not in allowed_sort_fields:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "sort_by không hợp lệ. "
                f"Cho phép: {', '.join(allowed_sort_fields)}"
            )
        )

    try:

        result = get_customers_service(
            db=db,
            page=page,
            page_size=page_size,
            search=search,
            area=area,
            sort_by=sort_by,
            sort_order=sort_order
        )

        total = (
            result[0]["total_count"]
            if result
            else 0
        )

        customers = []

        for row in result:

            customer = dict(row)

            customer.pop(
                "total_count",
                None
            )

            customers.append(
                customer
            )

        total_pages = (
            (total + page_size - 1)
            // page_size
            if total > 0
            else 0
        )

        return {
            "items": customers,
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages
        }

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =========================================================
# 4. ADMIN / NHÂN VIÊN KHÓA / MỞ KHÁCH HÀNG
# =========================================================

@router.patch(
    "/{customer_id}/status"
)
def change_customer_status(

    customer_id: int,

    data: CustomerStatusUpdate,

    current_user: User = Depends(
        require_roles(
            "Admin",
            "NhanVien"
        )
    ),

    db: Session = Depends(get_db)
):

    if data.status not in (
        "ACTIVE",
        "INACTIVE"
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Trạng thái chỉ được "
                "ACTIVE hoặc INACTIVE"
            )
        )

    try:

        change_customer_status_service(
            db=db,
            customer_id=customer_id,
            customer_status=data.status
        )

        return {
            "message":
                (
                    "Khóa khách hàng thành công"
                    if data.status == "INACTIVE"
                    else
                    "Mở khóa khách hàng thành công"
                )
        }

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )