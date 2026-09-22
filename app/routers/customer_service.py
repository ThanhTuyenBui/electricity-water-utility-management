from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    get_current_user,
    require_roles
)

from app.models.user import User

from app.schemas.customer_service import (
    CounterRegisterRequest,
    CustomerServiceActionResponse
)

from app.services.customer_service import (
    approve_customer_service,
    register_customer_at_counter
)


router = APIRouter(
    prefix="/customer-services",
    tags=["Customer Services"]
)


# ============================================================
# ADMIN - PHÊ DUYỆT ĐĂNG KÝ DỊCH VỤ
# ============================================================

@router.put(
    "/{customer_service_id}/approve",
    response_model=CustomerServiceActionResponse,
    dependencies=[Depends(require_roles("Admin"))]
)
def approve(
    customer_service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    approve_customer_service(
        db=db,
        customer_service_id=customer_service_id,
        admin_user_id=current_user.user_id
    )

    return {
        "message": "Đã phê duyệt đơn đăng ký dịch vụ",
        "user_id": None
    }


# ============================================================
# NHÂN VIÊN - ĐĂNG KÝ KHÁCH HÀNG TẠI QUẦY
# ============================================================

@router.post(
    "/counter-register",
    response_model=CustomerServiceActionResponse,
    status_code=201,
    dependencies=[Depends(require_roles("NhanVien"))]
)
def counter_register(
    data: CounterRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = register_customer_at_counter(
        db=db,
        username=data.username,
        password=data.password,
        email=data.email,
        full_name=data.full_name,
        service_ids=data.service_ids,
        employee_user_id=current_user.user_id,
        phone=data.phone,
        identity_number=data.identity_number,
        address=data.address
    )

    return {
        "message": "Đã tạo tài khoản khách hàng tại quầy",
        "user_id": user_id
    }