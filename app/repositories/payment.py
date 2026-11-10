from sqlalchemy import text
from sqlalchemy.orm import Session


def processBillPayment(
    db: Session,
    bill_id: int,
    user_id: int,
    transaction_code: str = None
):
    result = db.execute(
        text("""
            SELECT public.process_bill_payment(
                :p_bill_id,
                :p_user_id,
                :p_transaction_code
            )
        """),
        {
            "p_bill_id": bill_id,
            "p_user_id": user_id,
            "p_transaction_code": transaction_code
        }
    )

    return result.scalar()