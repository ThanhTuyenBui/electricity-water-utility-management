
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv(
    "GROQ_MODEL",
    "openai/gpt-oss-120b"
)

if not GROQ_API_KEY:
    raise RuntimeError(
        "Chưa cấu hình GROQ_API_KEY trong file .env"
    )

groq_client = Groq(
    api_key=GROQ_API_KEY,
    timeout=30.0,
    max_retries=1
)
