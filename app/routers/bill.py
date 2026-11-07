
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_db,
    require_roles
)

from app.schemas.bill import BillCalculationResponse

from app.services.bill import (
    calculate_bill,
    export_invoice_pdf
)


router = APIRouter()


# =========================================================
# 1. ADMIN / NHÂN VIÊN TÍNH TIỀN HÓA ĐƠN
# =========================================================

@router.post(
    "/{bill_id}/calculate",
    response_model=BillCalculationResponse
)
def calculate_bill_api(
    bill_id: int,
    current_user=Depends(
        require_roles("Admin", "NhanVien")
    ),
    db: Session = Depends(get_db)
):
    if bill_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="bill_id phải lớn hơn 0"
        )

    try:
        return calculate_bill(
            db=db,
            bill_id=bill_id
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# =========================================================
# 2. ADMIN / NHÂN VIÊN XUẤT HÓA ĐƠN PDF
# =========================================================

@router.get(
    "/{bill_id}/pdf",
    dependencies=[
        Depends(require_roles("Admin", "NhanVien"))
    ]
)
def export_invoice_pdf_api(
    bill_id: int,
    db: Session = Depends(get_db)
):
    if bill_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="bill_id phải lớn hơn 0"
        )

    try:
        result = export_invoice_pdf(
            db=db,
            bill_id=bill_id
        )

        project_root = Path(__file__).resolve().parents[2]
        file_path = project_root / result["pdf_url"]

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy file PDF"
            )

        return FileResponse(
            path=str(file_path),
            media_type="application/pdf",
            filename=f"{result['bill_code']}.pdf"
        )

    except HTTPException:
        raise

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
