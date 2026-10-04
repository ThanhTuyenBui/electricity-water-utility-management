from sqlalchemy import text
from sqlalchemy.orm import Session


def get_pending_customer_services(
    db: Session,
    page: int,
    page_size: int
):
    cursor_name = "pending_customer_services_cursor"

    db.execute(
        text("""
            CALL get_pending_customer_services(
                :page,
                :page_size,
                :cursor_name
            )
        """),
        {
            "page": page,
            "page_size": page_size,
            "cursor_name": cursor_name
        }
    )

    result = db.execute(
        text(f'FETCH ALL FROM "{cursor_name}"')
    )

    data = result.mappings().all()

    db.commit()

    return data


def get_customer_service_detail(
    db: Session,
    customer_id: int
):
    cursor_name = "customer_service_detail_cursor"

    db.execute(
        text("""
            CALL get_customer_service_detail(
                :customer_id,
                :cursor_name
            )
        """),
        {
            "customer_id": customer_id,
            "cursor_name": cursor_name
        }
    )

    result = db.execute(
        text(f'FETCH ALL FROM "{cursor_name}"')
    )

    # Lấy TẤT CẢ dịch vụ của khách hàng
    data = result.mappings().all()

    db.commit()

    return data


def approve_customer_services_by_customer(
    db: Session,
    customer_id: int,
    employee_user_id: int
):
    db.execute(
        text("""
            CALL approve_customer_services_by_customer(
                :customer_id,
                :employee_user_id
            )
        """),
        {
            "customer_id": customer_id,
            "employee_user_id": employee_user_id
        }
    )

    db.commit()

    return True


def reject_customer_services_by_customer(
    db: Session,
    customer_id: int,
    employee_user_id: int,
    reason: str
):
    db.execute(
        text("""
            CALL reject_customer_services_by_customer(
                :customer_id,
                :employee_user_id,
                :reason
            )
        """),
        {
            "customer_id": customer_id,
            "employee_user_id": employee_user_id,
            "reason": reason
        }
    )

    db.commit()

    return True


def request_stop_customer_service(
    db: Session,
    customer_service_id: int,
    customer_id: int
):
    db.execute(
        text("""
            CALL request_stop_customer_service(
                :customer_service_id,
                :customer_id
            )
        """),
        {
            "customer_service_id": customer_service_id,
            "customer_id": customer_id
        }
    )

    db.commit()

    return True


def get_pending_stop_customer_services(
    db: Session,
    page: int,
    page_size: int
):
    cursor_name = "pending_stop_customer_services_cursor"

    db.execute(
        text("""
            CALL get_pending_stop_customer_services(
                :page,
                :page_size,
                :cursor_name
            )
        """),
        {
            "page": page,
            "page_size": page_size,
            "cursor_name": cursor_name
        }
    )

    result = db.execute(
        text(f'FETCH ALL FROM "{cursor_name}"')
    )

    data = result.mappings().all()

    db.commit()

    return data


def stop_customer_service(
    db: Session,
    customer_service_id: int
):
    db.execute(
        text("""
            CALL stop_customer_service(
                :customer_service_id
            )
        """),
        {
            "customer_service_id": customer_service_id
        }
    )

    db.commit()

    return True


def register_customer_at_counter(
    db: Session,
    username: str,
    password_hash: str,
    email: str,
    full_name: str,
    service_ids: list[int],
    employee_user_id: int,
    phone: str | None = None,
    identity_number: str | None = None,
    address: str | None = None
):
    query = text("""
        SELECT register_customer_at_counter(
            :username,
            :password_hash,
            :email,
            :full_name,
            CAST(:service_ids AS BIGINT[]),
            :employee_user_id,
            :phone,
            :identity_number,
            :address
        )
    """)

    result = db.execute(
        query,
        {
            "username": username,
            "password_hash": password_hash,
            "email": email,
            "full_name": full_name,
            "service_ids": service_ids,
            "employee_user_id": employee_user_id,
            "phone": phone,
            "identity_number": identity_number,
            "address": address
        }
    )

    user_id = result.scalar()

    db.commit()

    return user_id
def register_additional_service(
    db: Session,
    customer_id: int,
    service_id: int,
    installation_address: str
):
    query = text("""
        SELECT register_additional_service(
            :customer_id,
            :service_id,
            :installation_address
        )
    """)

    result = db.execute(
        query,
        {
            "customer_id": customer_id,
            "service_id": service_id,
            "installation_address": installation_address
        }
    )

    customer_service_id = result.scalar()

    db.commit()

    return customer_service_id
def get_pending_customer_service_detail(
    db: Session,
    customer_id: int
):
    cursor_name = "pending_customer_service_detail_cursor"

    db.execute(text("""
        CALL get_pending_customer_service_detail(
            :customer_id,
            :cursor_name
        )
    """), {
        "customer_id": customer_id,
        "cursor_name": cursor_name
    })

    result = db.execute(
        text(f'FETCH ALL FROM "{cursor_name}"')
    )

    data = result.mappings().all()

    db.commit()

    return data


def get_pending_stop_customer_service_detail(
    db: Session,
    customer_id: int
):
    cursor_name = "pending_stop_customer_service_detail_cursor"

    db.execute(text("""
        CALL get_pending_stop_customer_service_detail(
            :customer_id,
            :cursor_name
        )
    """), {
        "customer_id": customer_id,
        "cursor_name": cursor_name
    })

    result = db.execute(
        text(f'FETCH ALL FROM "{cursor_name}"')
    )

    data = result.mappings().all()

    db.commit()

    return data