
import time
from app.core.ai_config import groq_client, GROQ_MODEL

print("Model:", GROQ_MODEL)
print("Đang gửi yêu cầu đến Groq...", flush=True)

start = time.time()

try:
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "Bạn là trợ lý AI, trả lời bằng tiếng Việt."
            },
            {
                "role": "user",
                "content": "Xin chào, hãy giới thiệu bản thân."
            }
        ],
        max_tokens=500
    )

    print("Thời gian phản hồi:", round(time.time() - start, 2), "giây")
    print("\nKẾT QUẢ:")
    print(response.choices[0].message.content)

except Exception as e:
    print("\nLOẠI LỖI:", type(e).__name__)
    print("CHI TIẾT:", str(e))
