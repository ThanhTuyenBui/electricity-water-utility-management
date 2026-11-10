from sqlalchemy.orm import Session

from app.repositories import debt_management


def get_customer_debt_summary_service(
    db: Session,
    customer_id: int | None = None
):
    if customer_id is not None and customer_id <= 0:
        raise ValueError("Customer ID không hợp lệ")

    return debt_management.get_customer_debt_summary(
        db=db,
        customer_id=customer_id
    )


def get_customer_debt_list_service(
    db: Session,
    page: int = 1,
    page_size: int = 10
):
    if page < 1:
        raise ValueError("Số trang phải lớn hơn hoặc bằng 1")

    if page_size < 1 or page_size > 100:
        raise ValueError("Page size phải nằm trong khoảng 1 đến 100")

    return debt_management.get_customer_debt_list(
        db=db,
        page=page,
        page_size=page_size
    )


def get_customers_with_debt_service(
    db: Session,
    page: int = 1,
    page_size: int = 10
):
    if page < 1:
        raise ValueError("Số trang phải lớn hơn hoặc bằng 1")

    if page_size < 1 or page_size > 100:
        raise ValueError("Page size phải nằm trong khoảng 1 đến 100")

    return debt_management.get_customers_with_debt(
        db=db,
        page=page,
        page_size=page_size
    )


def get_services_eligible_for_debt_suspension_service(db: Session):
    """Lấy danh sách dịch vụ đủ điều kiện tạm ngừng do nợ."""
    return debt_management.get_services_eligible_for_debt_suspension(
        db=db
    )



from sqlalchemy.exc import DBAPIError

def suspend_customer_service_for_debt_service(
    db: Session,
    customer_service_id: int,
    user_id: int,
    current_reading: int
):
    """Xác nhận tạm ngừng dịch vụ do nợ."""

    if customer_service_id <= 0:
        raise ValueError("ID đăng ký dịch vụ không hợp lệ.")

    if user_id <= 0:
        raise ValueError("ID nhân viên không hợp lệ.")

    if current_reading < 0:
        raise ValueError("Chỉ số công tơ không được âm.")

    try:
        debt_management.suspend_customer_service_for_debt(
            db=db,
            customer_service_id=customer_service_id,
            user_id=user_id,
            current_reading=current_reading
        )
        db.commit()

    except DBAPIError as e:
        db.rollback()

        original_error = str(e.orig)

        if "Chỉ số chốt" in original_error:
            raise ValueError(original_error.split("\n")[0].strip())

        raise

    except Exception:
        db.rollback()
        raise


def get_services_eligible_for_debt_restoration_service(db: Session):
    """Lấy danh sách dịch vụ đủ điều kiện khôi phục."""
    return debt_management.get_services_eligible_for_debt_restoration(
        db=db
    )


def restore_customer_service_after_debt_payment_service(
    db: Session,
    customer_service_id: int,
    user_id: int
):
    """Xác nhận khôi phục dịch vụ sau khi thanh toán hết nợ."""

    if customer_service_id <= 0:
        raise ValueError("ID đăng ký dịch vụ không hợp lệ.")

    if user_id <= 0:
        raise ValueError("ID nhân viên không hợp lệ.")

    try:
        debt_management.restore_customer_service_after_debt_payment(
            db=db,
            customer_service_id=customer_service_id,
            user_id=user_id
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
