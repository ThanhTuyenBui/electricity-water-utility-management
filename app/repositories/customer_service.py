from sqlalchemy import text
from sqlalchemy.orm import Session


def approve_customer_service(
    db: Session,
    customer_service_id: int,
    admin_user_id: int
):
    query = text("""
        SELECT approve_customer_service(
            :customer_service_id,
            :admin_user_id
        )
    """)

    result = db.execute(
        query,
        {
            "customer_service_id": customer_service_id,
            "admin_user_id": admin_user_id
        }
    )

    result.scalar()

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