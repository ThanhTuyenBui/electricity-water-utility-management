import resend

from app.core.config import settings


def send_reset_password_email(
    to_email: str,
    reset_token: str
):
    """
    Gửi email chứa link đặt lại mật khẩu.
    """

    resend.api_key = settings.RESEND_API_KEY

    reset_link = (
        "http://127.0.0.1:8000/api/auth/reset-password"
        f"?token={reset_token}"
    )

    params = {
        "from": settings.MAIL_FROM,
        "to": [to_email],
        "subject": "Đặt lại mật khẩu - Electric Water Management",
        "html": f"""
        <h2>Đặt lại mật khẩu</h2>

        <p>Bạn vừa yêu cầu đặt lại mật khẩu
        cho tài khoản Electric Water Management.</p>

        <p>Token đặt lại mật khẩu:</p>

        <p>
            <strong>{reset_token}</strong>
        </p>

        <p>Link đặt lại mật khẩu:</p>

        <p>
            <a href="{reset_link}">
                Đặt lại mật khẩu
            </a>
        </p>

        <p>Token có hiệu lực trong 15 phút.</p>

        <p>Nếu bạn không thực hiện yêu cầu này,
        hãy bỏ qua email.</p>
        """
    }

    return resend.Emails.send(params)