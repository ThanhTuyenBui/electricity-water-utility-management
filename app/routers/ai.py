
import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import (
    get_current_user,
    get_db,
    require_roles
)

from app.schemas.ai import ChatRequest, ChatResponse

from app.services.ai_service import chat_with_ai
from app.services.ai_data_service import get_ai_meter_readings_context

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Assistant"])


@router.get("/health")
def ai_health():
    return {
        "success": True,
        "message": "AI module is ready"
    }


@router.post(
    "/chat",
    response_model=ChatResponse,
    dependencies=[
        Depends(
            require_roles("Admin", "NhanVien", "KhachHang")
        )
    ]
)
def chat(
    request: ChatRequest,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        # Lấy dữ liệu nghiệp vụ theo quyền tài khoản
        data_context = get_ai_meter_readings_context(
            db=db,
            current_user=current_user
        )

        # Gửi câu hỏi và dữ liệu cho AI
        answer = chat_with_ai(
            message=request.message,
            data_context=data_context
        )

        return ChatResponse(reply=answer)

    except Exception as e:
        logger.exception(
            "AI request failed for user_id=%s",
            current_user.user_id
        )

        raise HTTPException(
            status_code=502,
            detail="Không thể xử lý yêu cầu AI."
        ) from e
