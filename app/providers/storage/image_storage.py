
from pathlib import Path
from uuid import uuid4

# Xác định thư mục gốc project
BASE_DIR = Path(__file__).resolve().parents[3]

# Thư mục lưu ảnh công tơ
METER_IMAGE_DIR = BASE_DIR / "media" / "meter_readings"

# Tạo thư mục nếu chưa tồn tại
METER_IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def save_meter_reading_image(
    image_data: bytes,
    content_type: str
):
    """
    Lưu ảnh công tơ và trả về URL.
    """

    extensions = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp"
    }

    extension = extensions.get(content_type)

    if not extension:
        raise ValueError("Định dạng ảnh không hợp lệ")

    filename = f"{uuid4().hex}{extension}"

    file_path = METER_IMAGE_DIR / filename

    with open(file_path, "wb") as file:
        file.write(image_data)

    return f"/media/meter_readings/{filename}"


def delete_meter_reading_image(image_url: str):
    """
    Xóa ảnh nếu quá trình ghi chỉ số thất bại.
    """

    if not image_url:
        return

    filename = Path(image_url).name

    if filename != image_url.split("/")[-1]:
        return

    file_path = METER_IMAGE_DIR / filename

    if file_path.exists() and file_path.is_file():
        file_path.unlink()
