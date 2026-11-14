
from pathlib import Path
from html import escape
from decimal import Decimal, InvalidOperation

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


# =====================================================
# 1. FONT TIẾNG VIỆT
# =====================================================

FONT_PATH = (
    Path(__file__).resolve().parents[1]
    / "static"
    / "fonts"
    / "arial.ttf"
)

if not FONT_PATH.exists():
    raise FileNotFoundError(f"Không tìm thấy font: {FONT_PATH}")

if "Arial" not in pdfmetrics.getRegisteredFontNames():
    pdfmetrics.registerFont(TTFont("Arial", str(FONT_PATH)))


# =====================================================
# 2. HÀM HỖ TRỢ
# =====================================================

def format_money(value):
    """Định dạng tiền Việt Nam."""
    return f"{float(value or 0):,.0f}".replace(",", ".") + " VNĐ"


def format_number(value):
    """Định dạng số."""
    return f"{float(value or 0):,.0f}".replace(",", ".")


def safe_text(value):
    """Escape nội dung HTML trong Paragraph."""
    return escape(str(value if value is not None else ""))


def format_date(value):
    """Định dạng ngày tháng."""
    if value is None:
        return ""

    if hasattr(value, "strftime"):
        return value.strftime("%d/%m/%Y")

    return str(value)


def decimal_value(value):
    """Chuyển giá trị về Decimal để so sánh VAT chính xác."""
    try:
        return Decimal(str(value or 0))
    except (InvalidOperation, ValueError, TypeError):
        return Decimal("0")


def make_info_paragraph(label, value, style):
    """Tạo dòng thông tin dạng Nhãn: Giá trị."""
    return Paragraph(
        f"<b>{safe_text(label)}:</b> {safe_text(value)}",
        style
    )


def make_split_summary(split, styles):
    """Tạo bảng tổng kết biểu giá, tất cả nội dung căn phải."""

    right_style = ParagraphStyle(
        name="SplitSummaryRight",
        fontName="Arial",
        fontSize=12,
        leading=17,
        alignment=TA_RIGHT,
    )

    data = [
        [
            Paragraph("<b>Tiền tiêu thụ</b>", right_style),
            Paragraph(
                f"<b>{format_money(split.get('subtotal'))}</b>",
                right_style,
            ),
        ],
        [
            Paragraph(
                f"Phí môi trường ({format_number(split.get('environment_fee_percent'))}%)",
                right_style,
            ),
            Paragraph(format_money(split.get("fee_amount")), right_style),
        ],
        [
            Paragraph(
                f"VAT ({format_number(split.get('vat_percent'))}%)",
                right_style,
            ),
            Paragraph(format_money(split.get("tax_amount")), right_style),
        ],
        [
            Paragraph("<b>Tổng biểu giá</b>", right_style),
            Paragraph(
                f"<b>{format_money(split.get('total_amount'))}</b>",
                right_style,
            ),
        ],
    ]

    table = Table(
        data,
        colWidths=[130 * mm, 40 * mm],
        hAlign="LEFT",
    )

    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), 12),

        # Căn phải tất cả nội dung trong tất cả các ô
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),

        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),

        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),

        ("LINEABOVE", (0, 0), (-1, 0), 0.5, colors.grey),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.grey),
    ]))

    return table

# =====================================================
# 3. TẠO PDF HÓA ĐƠN
# =====================================================

def generate_invoice_pdf(invoice: dict, output_path: str) -> str:

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=12 * mm,
        bottomMargin=15 * mm,
        title=f"Hoa don {invoice.get('bill_code', '')}",
    )

    styles = getSampleStyleSheet()

    # -------------------------------------------------
    # STYLE
    # -------------------------------------------------

    styles.add(ParagraphStyle(
        name="CompanyTitle",
        fontName="Arial",
        fontSize=20,
        leading=26,
        alignment=TA_CENTER,
        spaceAfter=10,
    ))

    styles.add(ParagraphStyle(
        name="InvoiceTitle",
        fontName="Arial",
        fontSize=24,
        leading=30,
        alignment=TA_CENTER,
        spaceAfter=10,
    ))

    styles.add(ParagraphStyle(
        name="NormalVietnamese",
        fontName="Arial",
        fontSize=14,
        leading=21,
        alignment=TA_LEFT,
    ))

    styles.add(ParagraphStyle(
        name="CenterVietnamese",
        fontName="Arial",
        fontSize=14,
        leading=20,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="RightVietnamese",
        fontName="Arial",
        fontSize=14,
        leading=20,
        alignment=TA_RIGHT,
    ))

    styles.add(ParagraphStyle(
        name="SmallVietnamese",
        fontName="Arial",
        fontSize=12,
        leading=17,
    ))

    styles.add(ParagraphStyle(
        name="TotalMoney",
        fontName="Arial",
        fontSize=17,
        leading=24,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=8,
    ))

    elements = []
    # =================================================
    # 4. XÁC ĐỊNH DỊCH VỤ
    # =================================================

    service_name = str(invoice.get("service_name") or "").lower()

    if "nước" in service_name:
        unit = "m³"
        consumption_name = "Lượng nước tiêu thụ"
        invoice_title = "GIẤY BÁO TIỀN NƯỚC"
    else:
        unit = "kWh"
        consumption_name = "Điện năng tiêu thụ"
        invoice_title = "GIẤY BÁO TIỀN ĐIỆN"

    meters = invoice.get("meters") or []

    # Tương thích với dữ liệu dạng cũ.
    if not meters:
        meters = [{
            "previous_reading": invoice.get("previous_reading", 0),
            "current_reading": invoice.get("current_reading", 0),
            "consumption": invoice.get("consumption", 0),
            "amount": invoice.get("amount", 0),
            "tariff_splits": [],
        }]

    # Lấy tất cả biểu giá của hóa đơn.
    all_splits = []

    for meter in meters:
        for split in meter.get("tariff_splits", []):
            all_splits.append(split)

    # Chỉ tổng kết riêng khi có nhiều biểu giá
    # và VAT của các biểu giá khác nhau.
    vat_values = {
        decimal_value(split.get("vat_percent"))
        for split in all_splits
    }

    show_split_summary = (
        len(all_splits) > 1
        and len(vat_values) > 1
    )

    # =================================================
    # 5. PHẦN ĐẦU HÓA ĐƠN
    # =================================================

    elements.append(Paragraph(
        "<b>CÔNG TY QUẢN LÝ ĐIỆN NƯỚC WE</b>",
        styles["CompanyTitle"],
    ))

    elements.append(Paragraph(
        f"<b>{invoice_title}</b>",
        styles["InvoiceTitle"],
    ))

    elements.append(Paragraph(
        f"Dịch vụ: {safe_text(invoice.get('service_name'))}",
        styles["CenterVietnamese"],
    ))

    elements.append(Spacer(1, 8))

    # Mã hóa đơn căn giữa.
    elements.append(Paragraph(
        f"<b>Mã hóa đơn: "
        f"{safe_text(invoice.get('bill_code'))}</b>",
        styles["CenterVietnamese"],
    ))

    elements.append(Spacer(1, 8))

    # =================================================
    # 6. THÔNG TIN HÓA ĐƠN VÀ KHÁCH HÀNG
    # =================================================

    info_items = [
        ("Kỳ hóa đơn", invoice.get("billing_period")),
        ("Mã khách hàng", invoice.get("customer_code")),
        ("Họ và tên", invoice.get("full_name")),
        ("Số điện thoại", invoice.get("phone")),
        ("Địa chỉ", invoice.get("address")),
    ]

    for label, value in info_items:
        elements.append(
            make_info_paragraph(
                label,
                value,
                styles["NormalVietnamese"],
            )
        )

        elements.append(Spacer(1, 3))

    elements.append(Spacer(1, 7))

    # =================================================
    # 7. CHỈ SỐ TIÊU THỤ - 3 CỘT NGANG
    # =================================================

    for meter in meters:

        reading_data = [
            [
                Paragraph("<b>Chỉ số cũ</b>", styles["CenterVietnamese"]),
                Paragraph("<b>Chỉ số mới</b>", styles["CenterVietnamese"]),
                Paragraph(
                    f"<b>{safe_text(consumption_name)}</b>",
                    styles["CenterVietnamese"],
                ),
            ],
            [
                Paragraph(
                    f"<b>{format_number(meter.get('previous_reading'))}</b>",
                    styles["CenterVietnamese"],
                ),
                Paragraph(
                    f"<b>{format_number(meter.get('current_reading'))}</b>",
                    styles["CenterVietnamese"],
                ),
                Paragraph(
                    f"<b>{format_number(meter.get('consumption'))} "
                    f"{unit}</b>",
                    styles["CenterVietnamese"],
                ),
            ],
        ]

        reading_table = Table(
            reading_data,
            colWidths=[170 * mm / 3] * 3,
        )

        reading_table.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Arial"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEABOVE", (0, 0), (-1, 0), 0.7, colors.grey),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        

        elements.append(reading_table)
        elements.append(Spacer(1, 8))

    # =================================================
    # 8. BẢNG TÍNH TIỀN THEO BẬC THANG
    # =================================================

    for meter in meters:

        tariff_splits = meter.get("tariff_splits", [])

        for split_index, split in enumerate(tariff_splits):

            tiers = split.get("tiers", [])

            tier_data = [[
                "Bậc",
                "Khoảng định mức",
                "Sản lượng",
                "Đơn giá",
                "Thành tiền",
            ]]

            for tier in tiers:

                from_value = tier.get("from_value")
                to_value = tier.get("to_value")

                if to_value is None:
                    range_text = (
                        f"Từ {format_number(from_value)} trở lên"
                    )
                else:
                    range_text = (
                        f"{format_number(from_value)}"
                        f" - {format_number(to_value)}"
                    )

                tier_data.append([
                    str(tier.get("tier_order", "")),
                    safe_text(range_text),
                    format_number(tier.get("consumption")),
                    format_money(tier.get("unit_price")),
                    format_money(tier.get("amount")),
                ])

            if tiers:

                tier_table = Table(
                    tier_data,
                    colWidths=[
                        12 * mm,
                        42 * mm,
                        28 * mm,
                        40 * mm,
                        48 * mm,
                    ],
                    repeatRows=1,
                )

                tier_table.setStyle(TableStyle([
                    ("FONTNAME", (0, 0), (-1, -1), "Arial"),
                    ("FONTSIZE", (0, 0), (-1, -1), 12),
                    ("BACKGROUND", (0, 0), (-1, 0),
                     colors.HexColor("#DCE6F1")),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]))
                

                elements.append(tier_table)

            else:
                elements.append(Paragraph(
                    "Chưa có dữ liệu chi tiết các bậc giá.",
                    styles["SmallVietnamese"],
                ))

            elements.append(Spacer(1, 5))

            # Chỉ hiện tổng kết riêng khi:
            # - Có nhiều biểu giá.
            # - VAT của các biểu giá khác nhau.
            if show_split_summary:

                elements.append(
                    make_split_summary(split, styles)
                )

                elements.append(Spacer(1, 8))

    # =================================================
    # 9. TỔNG HỢP TIỀN TOÀN HÓA ĐƠN
    # =================================================

    elements.append(Spacer(1, 5))

    payment_items = [
        ("Tiền tiêu thụ", invoice.get("subtotal")),
        ("Phí môi trường", invoice.get("fee_amount")),
        ("Thuế VAT", invoice.get("tax_amount")),
    ]

    for label, value in payment_items:

        elements.append(
            make_info_paragraph(
                label,
                format_money(value),
                styles["NormalVietnamese"],
            )
        )

        elements.append(Spacer(1, 4))

    # Tổng tiền căn trái.
    elements.append(Paragraph(
        f"<b>Tổng tiền: "
        f"{format_money(invoice.get('total_amount'))}</b>",
        styles["TotalMoney"],
    ))

    elements.append(Spacer(1, 10))

    # =================================================
    # 10. HẠN THANH TOÁN VÀ LỜI CẢM ƠN
    # =================================================

    elements.append(Paragraph(
        f"<b>Hạn thanh toán: "
        f"{format_date(invoice.get('due_date'))}</b>",
        styles["CenterVietnamese"],
    ))

    elements.append(Spacer(1, 8))

    elements.append(Paragraph(
        "Vui lòng thanh toán đúng hạn. "
        "Xin cảm ơn quý khách đã sử dụng dịch vụ!",
        styles["CenterVietnamese"],
    ))

    # =================================================
    # 11. XUẤT FILE PDF
    # =================================================

    doc.build(elements)

    return str(output_file)
