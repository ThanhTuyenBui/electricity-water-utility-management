from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    get_current_user,
    require_roles
)

from app.models.user import User

from app.schemas.customer_service import (
    CounterRegisterRequest,
    AdditionalServiceRequest,
    CustomerServiceActionResponse
)

from app.services.customer_service import (
    get_pending_customer_services,
    get_customer_service_detail,
    register_additional_service,
    approve_customer_services_by_customer,
    reject_customer_services_by_customer,
    request_stop_customer_service,
    get_pending_stop_customer_services,
    stop_customer_service,
    register_customer_at_counter,
    get_pending_customer_service_detail,
    get_pending_stop_customer_service_detail,
)


router = APIRouter(
    prefix="/customer-services",
    tags=["Customer Services"]
)


# =========================================================
# 1. LẤY DANH SÁCH DỊCH VỤ ĐANG CHỜ PHÊ DUYỆT
# =========================================================

@router.get(
    "/pending",
    dependencies=[Depends(require_roles("NhanVien"))]
)
def get_pending(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    return get_pending_customer_services(
        db=db,
        page=page,
        page_size=page_size
    )


# =========================================================
# 2. LẤY TẤT CẢ DỊCH VỤ CỦA KHÁCH HÀNG
# =========================================================

@router.get(
    "/customers/{customer_id}",
    dependencies=[Depends(require_roles("NhanVien"))]
)
def get_detail(
    customer_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = get_customer_service_detail(
            db=db,
            customer_id=customer_id
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="Khách hàng chưa có dịch vụ"
            )

        return result

    except HTTPException:
        raise

    except Exception as e:
        message = str(e)

        if "Không tìm thấy khách hàng" in message:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy khách hàng"
            )

        raise HTTPException(
            status_code=400,
            detail=message
        )


# =========================================================
# 3. KHÁCH HÀNG ĐĂNG KÝ THÊM DỊCH VỤ
# =========================================================

@router.post(
    "/additional",
    response_model=CustomerServiceActionResponse,
    status_code=201,
    dependencies=[Depends(require_roles("KhachHang"))]
)
def additional_service(
    data: AdditionalServiceRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""
            SELECT customer_id
            FROM customers
            WHERE user_id = :user_id
        """),
        {
            "user_id": current_user.user_id
        }
    )

    customer_id = result.scalar()

    if customer_id is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thông tin khách hàng"
        )

    try:
        customer_service_id = register_additional_service(
            db=db,
            customer_id=customer_id,
            service_id=data.service_id,
            installation_address=data.installation_address
        )

        return {
            "message": "Đã đăng ký dịch vụ, đang chờ phê duyệt",
            "user_id": customer_service_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# =========================================================
# 4. DUYỆT TẤT CẢ DỊCH VỤ ĐANG CHỜ CỦA KHÁCH HÀNG
# =========================================================

@router.put(
    "/customers/{customer_id}/approve",
    response_model=CustomerServiceActionResponse,
    dependencies=[Depends(require_roles("NhanVien", "Admin"))]
)
def approve_customer_services(
    customer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        approve_customer_services_by_customer(
            db=db,
            customer_id=customer_id,
            employee_user_id=current_user.user_id
        )

        return {
            "message": "Đã phê duyệt tất cả dịch vụ đang chờ của khách hàng",
            "user_id": None
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# =========================================================
# 5. TỪ CHỐI TẤT CẢ DỊCH VỤ ĐANG CHỜ CỦA KHÁCH HÀNG
# =========================================================

@router.put(
    "/customers/{customer_id}/reject",
    response_model=CustomerServiceActionResponse,
    dependencies=[Depends(require_roles("NhanVien", "Admin"))]
)
def reject_customer_services(
    customer_id: int,
    reason: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Lý do từ chối không được để trống"
        )

    try:
        reject_customer_services_by_customer(
            db=db,
            customer_id=customer_id,
            employee_user_id=current_user.user_id,
            reason=reason
        )

        return {
            "message": "Đã từ chối tất cả dịch vụ đang chờ của khách hàng",
            "user_id": None
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# =========================================================
# 6. ĐĂNG KÝ KHÁCH HÀNG TẠI QUẦY
# =========================================================

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
    try:
        user_id = register_customer_at_counter(
            db=db,
            username=data.username,
            email=str(data.email),
            full_name=data.full_name,
            service_ids=data.service_ids,
            employee_user_id=current_user.user_id,
            phone=data.phone,
            identity_number=data.identity_number,
            address=data.address
        )

        return {
            "message": "Đã tạo tài khoản khách hàng tại quầy và gửi mật khẩu tạm thời qua SMS",
            "user_id": user_id
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# =========================================================
# 7. KHÁCH HÀNG YÊU CẦU NGỪNG SỬ DỤNG DỊCH VỤ
# =========================================================

@router.put(
    "/{customer_service_id}/request-stop",
    response_model=CustomerServiceActionResponse,
    dependencies=[Depends(require_roles("KhachHang"))]
)
def request_stop(
    customer_service_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = db.execute(
        text("""
            SELECT customer_id
            FROM customers
            WHERE user_id = :user_id
        """),
        {
            "user_id": current_user.user_id
        }
    )

    customer_id = result.scalar()

    if customer_id is None:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy thông tin khách hàng"
        )

    try:
        request_stop_customer_service(
            db=db,
            customer_service_id=customer_service_id,
            customer_id=customer_id
        )

        return {
            "message": "Đã gửi yêu cầu ngừng sử dụng dịch vụ",
            "user_id": None
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# =========================================================
# 8. LẤY DANH SÁCH DỊCH VỤ ĐANG CHỜ NGỪNG
# =========================================================

@router.get(
    "/pending-stop",
    dependencies=[Depends(require_roles("NhanVien"))]
)
def get_pending_stop(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    return get_pending_stop_customer_services(
        db=db,
        page=page,
        page_size=page_size
    )


# =========================================================
# 9. NHÂN VIÊN XÁC NHẬN NGỪNG DỊCH VỤ
# =========================================================

@router.put(
    "/{customer_service_id}/stop",
    response_model=CustomerServiceActionResponse,
    dependencies=[Depends(require_roles("NhanVien"))]
)
def stop(
    customer_service_id: int,
    db: Session = Depends(get_db)
):
    try:
        stop_customer_service(
            db=db,
            customer_service_id=customer_service_id
        )

        return {
            "message": "Đã ngừng sử dụng dịch vụ",
            "user_id": None
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
@router.get(
    "/customers/{customer_id}/pending",
    dependencies=[Depends(require_roles("NhanVien"))]
)
def get_customer_pending_services(
    customer_id: int,
    db: Session = Depends(get_db)
):
    try:
        result = get_pending_customer_service_detail(
            db=db,
            customer_id=customer_id
        )

        return result

    except Exception as e:
        message = str(e)

        if "Không tìm thấy khách hàng" in message:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy khách hàng"
            )

        raise HTTPException(
            status_code=400,
            detail=message
        )    