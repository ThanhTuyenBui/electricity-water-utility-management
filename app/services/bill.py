
from pathlib import Path
import re

from sqlalchemy.orm import Session

from app.repositories import bill as bill_repository
from app.services.invoice_pdf import generate_invoice_pdf


def calculate_bill(db: Session, bill_id: int):
    """
    Xử lý nghiệp vụ tính tiền hóa đơn.
    """
    total_amount = bill_repository.calculate_bill(
        db=db,
        bill_id=bill_id
    )

    return {
        "bill_id": bill_id,
        "total_amount": total_amount,
        "message": "Tính tiền hóa đơn thành công"
    }


def export_invoice_pdf(db: Session, bill_id: int):
    """
    Xử lý nghiệp vụ xuất hóa đơn PDF.
    """

    try:
        # 1. Lấy dữ liệu hóa đơn
        invoice = bill_repository.get_invoice_data(
            db=db,
            bill_id=bill_id
        )

        if invoice is None:
            raise ValueError("Không tìm thấy hóa đơn")

        # 2. Tạo thư mục lưu PDF
        project_root = Path(__file__).resolve().parents[2]

        invoice_dir = project_root / "media" / "invoices"
        invoice_dir.mkdir(parents=True, exist_ok=True)

        # 3. Tạo tên file an toàn
        bill_code = re.sub(
            r"[^a-zA-Z0-9_-]",
            "_",
            str(invoice["bill_code"])
        )

        file_name = f"{bill_code}.pdf"
        output_path = invoice_dir / file_name

        # 4. Tạo file PDF
        generate_invoice_pdf(
            invoice=invoice,
            output_path=str(output_path)
        )

        # 5. Lưu đường dẫn tương đối vào database
        pdf_url = f"media/invoices/{file_name}"

        updated_id = bill_repository.update_bill_pdf_url(
            db=db,
            bill_id=bill_id,
            pdf_url=pdf_url
        )

        if updated_id is None:
            raise ValueError("Không thể cập nhật đường dẫn PDF")

        # 6. Commit transaction
        db.commit()

        return {
            "bill_id": bill_id,
            "bill_code": invoice["bill_code"],
            "pdf_url": pdf_url,
            "message": "Xuất hóa đơn PDF thành công"
        }

    except Exception:
        db.rollback()
        raise
