from sqlalchemy import text
from sqlalchemy.orm import Session


def get_customer_debt_summary(
    db: Session,
    customer_id: int | None = None
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_customer_debt_summary(
                :p_customer_id
            )
        """),
        {"p_customer_id": customer_id}
    )

    return [
        dict(row)
        for row in result.mappings().all()
    ]


def get_customer_debt_list(
    db: Session,
    page: int = 1,
    page_size: int = 10
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_customer_debt_list(
                :p_page,
                :p_page_size
            )
        """),
        {
            "p_page": page,
            "p_page_size": page_size
        }
    )

    return [
        dict(row)
        for row in result.mappings().all()
    ]


def get_customers_with_debt(
    db: Session,
    page: int = 1,
    page_size: int = 10
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_customers_with_debt(
                :p_page,
                :p_page_size
            )
        """),
        {
            "p_page": page,
            "p_page_size": page_size
        }
    )

    return [
        dict(row)
        for row in result.mappings().all()
    ]


def get_services_eligible_for_debt_suspension(db: Session):
    """Lấy danh sách dịch vụ đủ điều kiện tạm ngừng do nợ."""
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_services_eligible_for_debt_suspension()
        """)
    )

    return [dict(row) for row in result.mappings().all()]


def suspend_customer_service_for_debt(
    db: Session,
    customer_service_id: int,
    user_id: int,
    current_reading: int
):
    """Tạm ngừng dịch vụ do nợ và chốt chỉ số công tơ."""
    db.execute(
        text("""
            CALL public.suspend_customer_service_for_debt(
                :p_customer_service_id,
                :p_user_id,
                :p_current_reading
            )
        """),
        {
            "p_customer_service_id": customer_service_id,
            "p_user_id": user_id,
            "p_current_reading": current_reading
        }
    )


def get_services_eligible_for_debt_restoration(db: Session):
    """Lấy danh sách dịch vụ đủ điều kiện khôi phục."""
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_services_eligible_for_debt_restoration()
        """)
    )

    return [dict(row) for row in result.mappings().all()]


def restore_customer_service_after_debt_payment(
    db: Session,
    customer_service_id: int,
    user_id: int
):
    """Khôi phục dịch vụ sau khi khách hàng thanh toán hết nợ."""
    db.execute(
        text("""
            CALL public.restore_customer_service_after_debt_payment(
                :p_customer_service_id,
                :p_user_id
            )
        """),
        {
            "p_customer_service_id": customer_service_id,
            "p_user_id": user_id
        }
    )
