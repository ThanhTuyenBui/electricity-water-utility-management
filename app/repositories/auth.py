from sqlalchemy import text
from sqlalchemy.orm import Session


def register_customer(
    db: Session,
    username: str,
    password_hash: str,
    email: str,
    full_name: str,
    service_ids: list[int],
    phone: str | None = None,
    identity_number: str | None = None,
    address: str | None = None
):
    query = text("""
        SELECT register_customer(
            :username,
            :password_hash,
            :email,
            :full_name,
            CAST(:service_ids AS BIGINT[]),
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
            "phone": phone,
            "identity_number": identity_number,
            "address": address
        }
    )

    user_id = result.scalar()

    db.commit()

    return user_id