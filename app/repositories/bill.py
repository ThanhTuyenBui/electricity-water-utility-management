
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
    try:
        # 1. Lấy thông tin hóa đơn, khách hàng và dịch vụ
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
                    s.service_name
                FROM bills b
                JOIN customer_services cs
                    ON b.customer_service_id = cs.customer_service_id
                JOIN customers c
                    ON cs.customer_id = c.customer_id
                JOIN services s
                    ON cs.service_id = s.service_id
                WHERE b.bill_id = :bill_id
            """),
            {"bill_id": bill_id}
        )

        invoice_row = result.mappings().first()

        if invoice_row is None:
            return None

        invoice = dict(invoice_row)

        # 2. Lấy các công tơ và chỉ số thuộc hóa đơn
        result = db.execute(
            text("""
                SELECT
                    bd.detail_id,
                    bd.previous_reading,
                    bd.current_reading,
                    bd.consumption,
                    bd.amount,
                    m.meter_id,
                    m.serial_number,
                    m.meter_type
                FROM bill_details bd
                JOIN meters m
                    ON bd.meter_id = m.meter_id
                WHERE bd.bill_id = :bill_id
                ORDER BY m.meter_id
            """),
            {"bill_id": bill_id}
        )

        detail_rows = result.mappings().all()

        if not detail_rows:
            return None

        meters = []

        # 3. Lấy biểu giá và chi tiết từng bậc giá
        for detail_row in detail_rows:
            detail = dict(detail_row)

            result = db.execute(
                text("""
                    SELECT
                        tariff_split_id,
                        tariff_id,
                        start_date,
                        end_date,
                        total_days,
                        consumption,
                        subtotal,
                        environment_fee_percent,
                        fee_amount,
                        vat_percent,
                        tax_amount,
                        total_amount
                    FROM bill_detail_tariff_splits
                    WHERE detail_id = :detail_id
                    ORDER BY start_date, tariff_split_id
                """),
                {"detail_id": detail["detail_id"]}
            )

            split_rows = result.mappings().all()
            tariff_splits = []

            for split_row in split_rows:
                split = dict(split_row)

                result = db.execute(
                    text("""
                        SELECT
                            tier_order,
                            from_value,
                            to_value,
                            consumption,
                            unit_price,
                            amount,
                            adjusted_allowance
                        FROM bill_detail_tiers
                        WHERE tariff_split_id = :tariff_split_id
                        ORDER BY tier_order
                    """),
                    {"tariff_split_id": split["tariff_split_id"]}
                )

                split["tiers"] = [
                    dict(row) for row in result.mappings().all()
                ]

                tariff_splits.append(split)

            detail["tariff_splits"] = tariff_splits
            meters.append(detail)

        invoice["meters"] = meters

        # 4. Giữ các trường phẳng để tương thích PDF
        if meters:
            invoice.update({
                "meter_id": meters[0]["meter_id"],
                "serial_number": meters[0]["serial_number"],
                "meter_type": meters[0]["meter_type"],
                "previous_reading": meters[0]["previous_reading"],
                "current_reading": meters[0]["current_reading"],
                "consumption": meters[0]["consumption"],
                "amount": meters[0]["amount"],
            })

        return invoice

    except Exception:
        import traceback

        print("\n========== LOI GET_INVOICE_DATA ==========")
        print(f"Bill ID: {bill_id}")
        traceback.print_exc()
        print("==========================================\n")

        raise


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
