from sqlalchemy.orm import Session

from app.repositories.customer_service import (
    get_pending_customer_services as get_pending_customer_services_repo,
    get_customer_service_detail as get_customer_service_detail_repo,
    approve_customer_services_by_customer as approve_customer_services_by_customer_repo,
    reject_customer_services_by_customer as reject_customer_services_by_customer_repo,
    request_stop_customer_service as request_stop_customer_service_repo,
    get_pending_stop_customer_services as get_pending_stop_customer_services_repo,
    stop_customer_service as stop_customer_service_repo,
    register_customer_at_counter as register_customer_at_counter_repo,
    register_additional_service as register_additional_service_repo,
    get_pending_customer_service_detail as get_pending_customer_service_detail_repo,

get_pending_stop_customer_service_detail as get_pending_stop_customer_service_detail_repo,
)

from app.core.security import hash_password
from app.services.sms import SMSService

import secrets
import string


def generate_temporary_password(length: int = 10) -> str:
    characters = string.ascii_letters + string.digits

    return "".join(
        secrets.choice(characters)
        for _ in range(length)
    )


def get_pending_customer_services(
    db: Session,
    page: int,
    page_size: int
):
    return get_pending_customer_services_repo(
        db=db,
        page=page,
        page_size=page_size
    )


def get_customer_service_detail(
    db: Session,
    customer_id: int
):
    return get_customer_service_detail_repo(
        db=db,
        customer_id=customer_id
    )


def approve_customer_services_by_customer(
    db: Session,
    customer_id: int,
    employee_user_id: int
):
    return approve_customer_services_by_customer_repo(
        db=db,
        customer_id=customer_id,
        employee_user_id=employee_user_id
    )


def reject_customer_services_by_customer(
    db: Session,
    customer_id: int,
    employee_user_id: int,
    reason: str
):
    return reject_customer_services_by_customer_repo(
        db=db,
        customer_id=customer_id,
        employee_user_id=employee_user_id,
        reason=reason
    )


def request_stop_customer_service(
    db: Session,
    customer_service_id: int,
    customer_id: int
):
    return request_stop_customer_service_repo(
        db=db,
        customer_service_id=customer_service_id,
        customer_id=customer_id
    )


def get_pending_stop_customer_services(
    db: Session,
    page: int,
    page_size: int
):
    return get_pending_stop_customer_services_repo(
        db=db,
        page=page,
        page_size=page_size
    )


def stop_customer_service(
    db: Session,
    customer_service_id: int
):
    return stop_customer_service_repo(
        db=db,
        customer_service_id=customer_service_id
    )


def register_customer_at_counter(
    db: Session,
    username: str,
    email: str,
    full_name: str,
    service_ids: list[int],
    employee_user_id: int,
    phone: str | None = None,
    identity_number: str | None = None,
    address: str | None = None
):
    temporary_password = generate_temporary_password()

    password_hash = hash_password(
        temporary_password
    )

    try:
        user_id = register_customer_at_counter_repo(
            db=db,
            username=username,
            password_hash=password_hash,
            email=email,
            full_name=full_name,
            service_ids=service_ids,
            employee_user_id=employee_user_id,
            phone=phone,
            identity_number=identity_number,
            address=address
        )

        if phone:
            SMSService().send_customer_password(
                phone_number=phone,
                username=username,
                password=temporary_password
            )

        return user_id

    except Exception:
        db.rollback()
        raise
def register_additional_service(
    db: Session,
    customer_id: int,
    service_id: int,
    installation_address: str
):
    return register_additional_service_repo(
        db=db,
        customer_id=customer_id,
        service_id=service_id,
        installation_address=installation_address
    ) 
def get_pending_customer_service_detail(
    db,
    customer_id: int
):
    return get_pending_customer_service_detail_repo(
        db=db,
        customer_id=customer_id
    )


def get_pending_stop_customer_service_detail(
    db,
    customer_id: int
):
    return get_pending_stop_customer_service_detail_repo(
        db=db,
        customer_id=customer_id
    )  