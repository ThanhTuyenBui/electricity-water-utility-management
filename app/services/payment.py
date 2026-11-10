from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

from app.repositories import payment as payment_repository


def processBillPaymentService(
    db: Session,
    bill_id: int,
    user_id: int,
    transaction_code: str = None
):
    if bill_id <= 0:
        raise ValueError("ID hóa đơn không hợp lệ.")

    if user_id <= 0:
        raise ValueError("ID tài khoản không hợp lệ.")

    if transaction_code is not None:
        transaction_code = transaction_code.strip()

        if not transaction_code:
            transaction_code = None

    try:
        payment_id = payment_repository.processBillPayment(
            db=db,
            bill_id=bill_id,
            user_id=user_id,
            transaction_code=transaction_code
        )

        db.commit()

        return payment_id

    except DBAPIError:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise