
from app.core.ai_config import gemini_client

print("Đang kiểm tra danh sách model Gemini...", flush=True)

try:
    models = gemini_client.models.list()

    count = 0
    for model in models:
        print("Model:", model.name)
        count += 1

        if count >= 15:
            break

    if count == 0:
        print("Không tìm thấy model nào.")

except Exception as e:
    print("\nLOẠI LỖI:", type(e).__name__)
    print("CHI TIẾT:", str(e))
