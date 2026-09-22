from sqlalchemy import text
from sqlalchemy.orm import Session


# =========================================================
# 1. THÊM NHÂN VIÊN
# =========================================================

def create_employee(
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
    db.execute(
        text("""
            CALL register_employee(
                :username,
                :password_hash,
                :employee_code,
                :full_name,
                :phone,
                :department,
                :position,
                :assigned_area
            )
        """),
        {
            "username": username,
            "password_hash": password_hash,
            "employee_code": employee_code,
            "full_name": full_name,
            "phone": phone,
            "department": department,
            "position": position,
            "assigned_area": assigned_area
        }
    )


# =========================================================
# 2. LẤY DANH SÁCH NHÂN VIÊN
# =========================================================

def get_all_employees(
    db: Session,
    page: int,
    page_size: int
):
    result = db.execute(
        text("""
            SELECT *
            FROM get_all_employees(
                :page,
                :page_size
            )
        """),
        {
            "page": page,
            "page_size": page_size
        }
    )

    return result.mappings().all()


# =========================================================
# 3. LẤY NHÂN VIÊN THEO ID
# =========================================================

def get_employee_by_id(
    db: Session,
    employee_id: int
):
    result = db.execute(
        text("""
            SELECT *
            FROM get_employee_by_id(
                :employee_id
            )
        """),
        {
            "employee_id": employee_id
        }
    )

    return result.mappings().first()


# =========================================================
# 4. CẬP NHẬT THÔNG TIN NHÂN VIÊN - ADMIN
# =========================================================

def update_employee(
    db: Session,
    employee_id: int,
    full_name: str | None,
    phone: str | None,
    department: str | None,
    position: str | None,
    assigned_area: str | None
):
    db.execute(
        text("""
            CALL update_employee(
                :employee_id,
                :full_name,
                :phone,
                :department,
                :position,
                :assigned_area
            )
        """),
        {
            "employee_id": employee_id,
            "full_name": full_name,
            "phone": phone,
            "department": department,
            "position": position,
            "assigned_area": assigned_area
        }
    )


# =========================================================
# 5. THAY ĐỔI TRẠNG THÁI NHÂN VIÊN - ADMIN
# =========================================================

def change_employee_status(
    db: Session,
    employee_id: int,
    employee_status: str
):
    db.execute(
        text("""
            CALL change_employee_status(
                :employee_id,
                :status
            )
        """),
        {
            "employee_id": employee_id,
            "status": employee_status
        }
    )


# =========================================================
# 6. NHÂN VIÊN XEM THÔNG TIN CỦA CHÍNH MÌNH
# =========================================================

def get_my_employee(
    db: Session,
    user_id: int
):
    result = db.execute(
        text("""
            SELECT *
            FROM get_employee_by_user_id(
                :user_id
            )
        """),
        {
            "user_id": user_id
        }
    )

    return result.mappings().first()
def update_my_employee(
    db: Session,
    user_id: int,
    full_name: str | None,
    phone: str | None
):
    db.execute(
        text("""
            CALL update_my_employee_profile(
                :user_id,
                :full_name,
                :phone
            )
        """),
        {
            "user_id": user_id,
            "full_name": full_name,
            "phone": phone
        }
    )