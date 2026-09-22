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

from app.core.security import hash_password

from app.models.user import User

from app.schemas.employee import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeeStatusUpdate,
    EmployeeResponse,
    EmployeeSelfUpdate
)

from app.services.employee import (
    create_employee_service,
    get_all_employees_service,
    get_employee_by_id_service,
    update_employee_service,
    change_employee_status_service,
    get_my_employee_service,
    update_my_employee_service
)


router = APIRouter()


# =========================================================
# 1. ADMIN - THÊM NHÂN VIÊN
# =========================================================

@router.post(
    "/",
    status_code=status.HTTP_201_CREATED
)
def create_employee(
    data: EmployeeCreate,

    current_user: User = Depends(
        require_roles("Admin")
    ),

    db: Session = Depends(get_db)
):
    """
    Chỉ Admin được phép tạo nhân viên.
    """

    password_hash = hash_password(
        data.password
    )

    try:

        create_employee_service(
            db=db,
            username=data.username,
            password_hash=password_hash,
            employee_code=data.employee_code,
            full_name=data.full_name,
            phone=data.phone,
            department=data.department,
            position=data.position,
            assigned_area=data.assigned_area
        )

        return {
            "message": "Tạo nhân viên thành công"
        }

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =========================================================
# 2. ADMIN - XEM DANH SÁCH NHÂN VIÊN
# =========================================================

@router.get("/")
def get_employees(
    page: int = Query(
        1,
        ge=1
    ),

    page_size: int = Query(
        10,
        ge=1,
        le=100
    ),

    current_user: User = Depends(
        require_roles("Admin")
    ),

    db: Session = Depends(get_db)
):
    """
    Chỉ Admin được xem danh sách nhân viên.
    """

    try:

        result = get_all_employees_service(
            db=db,
            page=page,
            page_size=page_size
        )

        total = (
            result[0]["total_count"]
            if result
            else 0
        )

        employees = []

        for row in result:

            employee = dict(row)

            employee.pop(
                "total_count",
                None
            )

            employees.append(
                employee
            )

        total_pages = (
            (total + page_size - 1)
            // page_size
            if total > 0
            else 0
        )

        return {
            "items": employees,
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
# 3. XEM THÔNG TIN CỦA CHÍNH MÌNH
# =========================================================

@router.get(
    "/me",
    response_model=EmployeeResponse
)
def get_my_employee(
    current_user: User = Depends(
        require_roles("Admin", "NhanVien")
    ),

    db: Session = Depends(get_db)
):
    """
    Admin và NhânVien được xem thông tin của chính mình.
    """

    result = get_my_employee_service(
        db=db,
        user_id=current_user.user_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin nhân viên"
        )

    return result


# =========================================================
# 4. SỬA THÔNG TIN CỦA CHÍNH MÌNH
# =========================================================

@router.put(
    "/me",
    response_model=EmployeeResponse
)
def update_my_employee(
    data: EmployeeSelfUpdate,

    current_user: User = Depends(
        require_roles("Admin", "NhanVien")
    ),

    db: Session = Depends(get_db)
):
    """
    Admin và NhânVien được sửa thông tin của chính mình.

    Chỉ cho phép sửa:
    - full_name
    - phone
    """

    update_data = data.model_dump(
        exclude_unset=True
    )

    try:

        update_my_employee_service(
            db=db,
            user_id=current_user.user_id,
            full_name=update_data.get("full_name"),
            phone=update_data.get("phone")
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    result = get_my_employee_service(
        db=db,
        user_id=current_user.user_id
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy thông tin nhân viên"
        )

    return result


# =========================================================
# 5. ADMIN - XEM CHI TIẾT NHÂN VIÊN
# =========================================================

@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def get_employee(
    employee_id: int,

    current_user: User = Depends(
        require_roles("Admin")
    ),

    db: Session = Depends(get_db)
):
    """
    Chỉ Admin được xem thông tin nhân viên theo ID.
    """

    result = get_employee_by_id_service(
        db=db,
        employee_id=employee_id
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy nhân viên"
        )

    return result


# =========================================================
# 6. ADMIN - CẬP NHẬT NHÂN VIÊN
# =========================================================

@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse
)
def update_employee(
    employee_id: int,

    data: EmployeeUpdate,

    current_user: User = Depends(
        require_roles("Admin")
    ),

    db: Session = Depends(get_db)
):
    """
    Chỉ Admin được cập nhật thông tin nhân viên.
    """

    update_data = data.model_dump(
        exclude_unset=True
    )

    try:

        update_employee_service(
            db=db,
            employee_id=employee_id,
            full_name=update_data.get("full_name"),
            phone=update_data.get("phone"),
            department=update_data.get("department"),
            position=update_data.get("position"),
            assigned_area=update_data.get("assigned_area")
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    result = get_employee_by_id_service(
        db=db,
        employee_id=employee_id
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy nhân viên"
        )

    return result
# =========================================================
# 7. ADMIN - THAY ĐỔI TRẠNG THÁI NHÂN VIÊN
# =========================================================

@router.patch(
    "/{employee_id}/status",
    response_model=EmployeeResponse
)
def change_employee_status(
    employee_id: int,

    data: EmployeeStatusUpdate,

    current_user: User = Depends(
        require_roles("Admin")
    ),

    db: Session = Depends(get_db)
):
    """
    Chỉ Admin được thay đổi trạng thái nhân viên.

    Trạng thái:
    - ACTIVE
    - INACTIVE
    """

    if data.status not in (
        "ACTIVE",
        "INACTIVE"
    ):

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trạng thái chỉ được ACTIVE hoặc INACTIVE"
        )

    try:

        change_employee_status_service(
            db=db,
            employee_id=employee_id,
            employee_status=data.status
        )

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    result = get_employee_by_id_service(
        db=db,
        employee_id=employee_id
    )

    if result is None:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy nhân viên"
        )

    return result