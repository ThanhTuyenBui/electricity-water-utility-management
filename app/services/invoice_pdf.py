
from pathlib import Path
from html import escape

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


# Đường dẫn font Arial hỗ trợ tiếng Việt
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


def format_money(value):
    """Định dạng tiền Việt Nam."""
    return f"{float(value or 0):,.0f}".replace(",", ".") + " VNĐ"


def safe_text(value):
    """Tránh lỗi khi dữ liệu chứa ký tự đặc biệt của HTML."""
    return escape(str(value if value is not None else ""))


def generate_invoice_pdf(invoice: dict, output_path: str) -> str:
    """
    Tạo hóa đơn PDF điện/nước.

    Parameters:
        invoice: Dictionary chứa thông tin hóa đơn.
        output_path: Đường dẫn lưu file PDF.

    Returns:
        Đường dẫn file PDF đã tạo.
    """

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(output_file),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="InvoiceTitle",
        fontName="Arial",
        fontSize=18,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=8,
    ))

    styles.add(ParagraphStyle(
        name="SectionTitle",
        fontName="Arial",
        fontSize=11,
        leading=16,
        spaceBefore=8,
        spaceAfter=6,
    ))

    styles.add(ParagraphStyle(
        name="NormalVietnamese",
        fontName="Arial",
        fontSize=9,
        leading=14,
    ))

    styles.add(ParagraphStyle(
        name="CenterVietnamese",
        fontName="Arial",
        fontSize=9,
        leading=14,
        alignment=TA_CENTER,
    ))

    styles.add(ParagraphStyle(
        name="RightVietnamese",
        fontName="Arial",
        fontSize=9,
        leading=14,
        alignment=TA_RIGHT,
    ))

    elements = []

    # Xác định loại dịch vụ và đơn vị tiêu thụ
    service_name = str(invoice.get("service_name", "")).lower()

    if "nước" in service_name:
        unit = "m³"
        consumption_name = "Lượng nước tiêu thụ"
    else:
        unit = "kWh"
        consumption_name = "Điện năng tiêu thụ"

    # Tiêu đề
    elements.append(Paragraph(
        "HÓA ĐƠN THANH TOÁN",
        styles["InvoiceTitle"]
    ))

    elements.append(Paragraph(
        f"<b>{safe_text(invoice.get('service_name'))}</b>",
        styles["CenterVietnamese"]
    ))

    elements.append(Spacer(1, 8))

    # Thông tin hóa đơn
    elements.append(Paragraph(
        "I. THÔNG TIN HÓA ĐƠN",
        styles["SectionTitle"]
    ))

    invoice_info = [
        ["Mã hóa đơn:", safe_text(invoice.get("bill_code"))],
        ["Kỳ hóa đơn:", safe_text(invoice.get("billing_period"))],
        ["Ngày phát hành:", str(invoice.get("issue_date", ""))],
        ["Hạn thanh toán:", str(invoice.get("due_date", ""))],
        ["Trạng thái:", safe_text(invoice.get("status"))],
    ]

    info_table = Table(
        invoice_info,
        colWidths=[45 * mm, 115 * mm]
    )

    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(info_table)

    # Thông tin khách hàng
    elements.append(Paragraph(
        "II. THÔNG TIN KHÁCH HÀNG",
        styles["SectionTitle"]
    ))

    customer_info = [
        ["Mã khách hàng:", safe_text(invoice.get("customer_code"))],
        ["Họ và tên:", safe_text(invoice.get("full_name"))],
        ["Số điện thoại:", safe_text(invoice.get("phone"))],
        ["Địa chỉ:", safe_text(invoice.get("address"))],
        ["Mã công tơ:", safe_text(invoice.get("serial_number"))],
    ]

    customer_table = Table(
        customer_info,
        colWidths=[45 * mm, 115 * mm]
    )

    customer_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))

    elements.append(customer_table)

    # Chi tiết tiêu thụ
    elements.append(Paragraph(
        "III. CHI TIẾT TIÊU THỤ",
        styles["SectionTitle"]
    ))

    consumption_data = [
        ["Chỉ số cũ", "Chỉ số mới", "Tiêu thụ", "Đơn vị"],
        [
            str(invoice.get("previous_reading", 0)),
            str(invoice.get("current_reading", 0)),
            str(invoice.get("consumption", 0)),
            unit,
        ],
    ]

    consumption_table = Table(
        consumption_data,
        colWidths=[40 * mm, 40 * mm, 40 * mm, 40 * mm]
    )

    consumption_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))

    elements.append(consumption_table)

    # Tổng hợp thanh toán
    elements.append(Paragraph(
        "IV. TỔNG HỢP THANH TOÁN",
        styles["SectionTitle"]
    ))

    payment_data = [
        ["Khoản mục", "Số tiền"],
        ["Tiền tiêu thụ", format_money(invoice.get("subtotal"))],
        ["Phí môi trường", format_money(invoice.get("fee_amount"))],
        ["Thuế VAT", format_money(invoice.get("tax_amount"))],
        ["TỔNG THANH TOÁN", format_money(invoice.get("total_amount"))],
    ]

    payment_table = Table(
        payment_data,
        colWidths=[95 * mm, 65 * mm]
    )

    payment_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Arial"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
        ("ALIGN", (1, 1), (1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E2F0D9")),
        ("FONTNAME", (0, -1), (-1, -1), "Arial"),
    ]))

    elements.append(payment_table)

    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        f"<b>{consumption_name}: "
        f"{safe_text(invoice.get('consumption', 0))} {unit}</b>",
        styles["RightVietnamese"]
    ))

    elements.append(Spacer(1, 12))

    elements.append(Paragraph(
        "Vui lòng thanh toán đúng hạn. "
        "Xin cảm ơn quý khách đã sử dụng dịch vụ!",
        styles["CenterVietnamese"]
    ))

    # Xuất PDF
    doc.build(elements)

    return str(output_file)
