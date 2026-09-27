from sqlalchemy.orm import Session

from app.repositories.customer import (
    get_my_customer,
    update_customer_self,
    get_customers,
    change_customer_status
)


# =========================================================
# 1. KHÁCH HÀNG XEM THÔNG TIN CỦA MÌNH
# =========================================================

def get_my_customer_service(
    db: Session,
    user_id: int
):

    return get_my_customer(
        db=db,
        user_id=user_id
    )


# =========================================================
# 2. KHÁCH HÀNG SỬA THÔNG TIN
# =========================================================

def update_customer_self_service(
    db: Session,
    user_id: int,
    full_name: str | None,
    phone: str | None,
    identity_number: str | None
):

    try:

        update_customer_self(
            db=db,
            user_id=user_id,
            full_name=full_name,
            phone=phone,
            identity_number=identity_number
        )

        db.commit()

    except Exception:

        db.rollback()
        raise


# =========================================================
# 3. DANH SÁCH KHÁCH HÀNG
# =========================================================

def get_customers_service(
    db: Session,
    page: int,
    page_size: int,
    search: str | None,
    area: str | None,
    sort_by: str,
    sort_order: str
):

    return get_customers(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        area=area,
        sort_by=sort_by,
        sort_order=sort_order
    )


# =========================================================
# 4. KHÓA / MỞ KHÁCH HÀNG
# =========================================================

def change_customer_status_service(
    db: Session,
    customer_id: int,
    customer_status: str
):

    try:

        result = change_customer_status(
            db=db,
            customer_id=customer_id,
            customer_status=customer_status
        )

        db.commit()

        return result

    except Exception:

        db.rollback()
        raise