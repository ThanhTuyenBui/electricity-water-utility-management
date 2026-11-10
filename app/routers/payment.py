from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

from app.core.dependencies import get_db, require_roles, get_current_user
from app.services import payment as payment_service
from app.schemas.payment import PaymentCreate


router = APIRouter()


# API khách hàng xác nhận thanh toán hóa đơn
@router.post(
    "/",
    dependencies=[Depends(require_roles("KhachHang"))]
)
def process_bill_payment(
    data: PaymentCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        payment_id = payment_service.processBillPaymentService(
            db=db,
            bill_id=data.bill_id,
            user_id=current_user.user_id,
            transaction_code=data.transaction_code
        )

        return {
            "message": "Thanh toán hóa đơn thành công.",
            "payment_id": payment_id,
            "bill_id": data.bill_id,
            "status": "CONFIRMED"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except DBAPIError:
        raise HTTPException(
            status_code=400,
            detail="Không thể thực hiện thanh toán. Vui lòng kiểm tra lại hóa đơn."
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Đã xảy ra lỗi trong quá trình thanh toán."
        )