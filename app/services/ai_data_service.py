
from app.services.meter import get_meter_readings


def get_ai_meter_readings_context(
    db,
    current_user,
    page_size: int = 12
):
    """
    Lấy dữ liệu chỉ số công tơ làm ngữ cảnh cho AI.

    Quyền truy cập được kế thừa từ Meter Service:
    - Admin: dữ liệu theo quyền hiện có.
    - NhanVien: dữ liệu theo quyền hiện có.
    - KhachHang: chỉ dữ liệu thuộc khách hàng đang đăng nhập.
    """

    result = get_meter_readings(
        db=db,
        current_user=current_user,
        page=1,
        page_size=page_size
    )

    items = result.get("items", [])

    readings = []

    for item in items:
        readings.append({
            "serial_number": item.get("serial_number"),
            "reading_period": item.get("reading_period"),
            "previous_reading": item.get("previous_reading"),
            "current_reading": item.get("current_reading"),
            "consumption": item.get("consumption"),
            "reading_date": str(item.get("reading_date"))
            if item.get("reading_date") else None
        })

    return {
        "total": result.get("total", 0),
        "readings": readings
    } 
