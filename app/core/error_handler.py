
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError


def handle_database_error(db, exc):
    db.rollback()

    if isinstance(exc, HTTPException):
        raise exc

    if isinstance(exc, SQLAlchemyError):
        original_error = getattr(exc, "orig", None)
        diagnostic = getattr(original_error, "diag", None)

        message = (
            getattr(diagnostic, "message_primary", None)
            if diagnostic else None
        )

        if not message and original_error:
            message = str(original_error).split("CONTEXT:")[0]
            message = message.split("\nDETAIL:")[0]
            message = message.replace("ERROR:", "").strip()

        if not message:
            message = "Đã xảy ra lỗi khi xử lý dữ liệu"

        raise HTTPException(
            status_code=400,
            detail=message
        ) from None

    raise HTTPException(
        status_code=500,
        detail="Đã xảy ra lỗi hệ thống"
    ) from None
