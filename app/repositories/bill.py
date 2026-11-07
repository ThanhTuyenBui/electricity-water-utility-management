
from sqlalchemy import text
from sqlalchemy.orm import Session


def calculate_bill(db: Session, bill_id: int):
    """
    Tính tiền hóa đơn thông qua hàm PostgreSQL.
    Dành cho API tính hóa đơn thủ công.
    """
    try:
        result = db.execute(
            text("""
                SELECT process_bill_calculation(:bill_id)
            """),
            {"bill_id": bill_id}
        )

        total_amount = result.scalar_one()

        db.commit()

        return total_amount

    except Exception:
        db.rollback()
        raise


def process_bill_calculation(db: Session, bill_id: int):
    """
    Tính tiền hóa đơn trong transaction hiện tại.
    Dùng khi tích hợp tự động sau khi ghi chỉ số công tơ.
    Không commit hoặc rollback tại repository.
    """
    result = db.execute(
        text("""
            SELECT process_bill_calculation(:bill_id)
        """),
        {"bill_id": bill_id}
    )

    return result.scalar_one()


def get_invoice_data(db: Session, bill_id: int):
    """
    Lấy thông tin hóa đơn, khách hàng, dịch vụ và công tơ
    phục vụ chức năng xuất hóa đơn PDF.
    """
    result = db.execute(
        text("""
            SELECT
                b.bill_id,
                b.bill_code,
                b.billing_period,
                b.issue_date,
                b.due_date,
                b.status,

                b.subtotal,
                b.fee_amount,
                b.tax_amount,
                b.total_amount,

                c.customer_code,
                c.full_name,
                c.phone,
                c.address,

                s.service_name,

                m.meter_id,
                m.serial_number,
                m.meter_type,

                bd.previous_reading,
                bd.current_reading,
                bd.consumption,
                bd.amount

            FROM bills b

            JOIN customer_services cs
                ON b.customer_service_id = cs.customer_service_id

            JOIN customers c
                ON cs.customer_id = c.customer_id

            JOIN services s
                ON cs.service_id = s.service_id

            JOIN bill_details bd
                ON b.bill_id = bd.bill_id

            JOIN meters m
                ON bd.meter_id = m.meter_id

            WHERE b.bill_id = :bill_id

            ORDER BY m.meter_id
        """),
        {"bill_id": bill_id}
    )

    rows = result.mappings().all()

    if not rows:
        return None

    # Tạm thời mỗi hóa đơn sử dụng một công tơ.
    # Nếu có nhiều công tơ, cần điều chỉnh mẫu PDF để hiển thị nhiều dòng.
    return dict(rows[0])


def update_bill_pdf_url(db: Session, bill_id: int, pdf_url: str):
    """
    Cập nhật đường dẫn file PDF vào hóa đơn.
    Không commit tại repository.
    """
    result = db.execute(
        text("""
            UPDATE bills
            SET pdf_url = :pdf_url,
                updated_at = CURRENT_TIMESTAMP
            WHERE bill_id = :bill_id
            RETURNING bill_id
        """),
        {
            "bill_id": bill_id,
            "pdf_url": pdf_url
        }
    )

    return result.scalar_one_or_none()
