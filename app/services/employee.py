from sqlalchemy.orm import Session

from app.repositories.employee import (
    create_employee,
    get_all_employees,
    get_employee_by_id,
    update_employee,
    change_employee_status,
    get_my_employee,
    update_my_employee
)


# =========================================================
# 1. TẠO NHÂN VIÊN
# =========================================================

def create_employee_service(
    db: Session,
    username: str,
    password_hash: str,
    employee_code: str,
    full_name: str,
    phone: str | None,
    department: str | None,
    position: str | None,
    assigned_area: str | None
):
    try:

        create_employee(
            db=db,
            username=username,
            password_hash=password_hash,
            employee_code=employee_code,
            full_name=full_name,
            phone=phone,
            department=department,
            position=position,
            assigned_area=assigned_area
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


# =========================================================
# 2. LẤY DANH SÁCH NHÂN VIÊN
# =========================================================

def get_all_employees_service(
    db: Session,
    page: int,
    page_size: int
):
    return get_all_employees(
        db=db,
        page=page,
        page_size=page_size
    )


# =========================================================
# 3. LẤY NHÂN VIÊN THEO ID
# =========================================================

def get_employee_by_id_service(
    db: Session,
    employee_id: int
):
    return get_employee_by_id(
        db=db,
        employee_id=employee_id
    )


# =========================================================
# 4. CẬP NHẬT NHÂN VIÊN - ADMIN
# =========================================================

def update_employee_service(
    db: Session,
    employee_id: int,
    full_name: str | None,
    phone: str | None,
    department: str | None,
    position: str | None,
    assigned_area: str | None
):
    try:

        update_employee(
            db=db,
            employee_id=employee_id,
            full_name=full_name,
            phone=phone,
            department=department,
            position=position,
            assigned_area=assigned_area
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


# =========================================================
# 5. THAY ĐỔI TRẠNG THÁI NHÂN VIÊN - ADMIN
# =========================================================

def change_employee_status_service(
    db: Session,
    employee_id: int,
    employee_status: str
):
    try:

        change_employee_status(
            db=db,
            employee_id=employee_id,
            employee_status=employee_status
        )

        db.commit()

    except Exception:
        db.rollback()
        raise


# =========================================================
# 6. NHÂN VIÊN XEM THÔNG TIN CỦA CHÍNH MÌNH
# =========================================================

def get_my_employee_service(
    db: Session,
    user_id: int
):
    return get_my_employee(
        db=db,
        user_id=user_id
    )

def update_my_employee_service(
    db: Session,
    user_id: int,
    full_name: str | None,
    phone: str | None
):
    try:
        update_my_employee(
            db=db,
            user_id=user_id,
            full_name=full_name,
            phone=phone
        )

        db.commit()

    except Exception:
        db.rollback()
        raise