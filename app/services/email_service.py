import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_reset_password_email(
    to_email: str,
    reset_token: str
):
    """
    Gửi email đặt lại mật khẩu bằng Gmail SMTP.
    """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Đặt lại mật khẩu</title>
    </head>

    <body>

        <h2>Đặt lại mật khẩu</h2>

        <p>
            Bạn vừa yêu cầu đặt lại mật khẩu
            cho tài khoản Electric Water Management.
        </p>

        <p>
            Mã đặt lại mật khẩu của bạn:
        </p>

        <p>
            <strong>{reset_token}</strong>
        </p>

        <p>
            Token có hiệu lực trong
            <strong>15 phút</strong>.
        </p>

        <p>
            Sau này hệ thống sẽ cung cấp
            trang đặt lại mật khẩu để bạn sử dụng token này.
        </p>

        <hr>

        <p>
            Electric Water Management
        </p>

    </body>
    </html>
    """

    message = MIMEMultipart("alternative")

    message["Subject"] = (
        "Đặt lại mật khẩu - Electric Water Management"
    )

    message["From"] = settings.MAIL_FROM
    message["To"] = to_email

    message.attach(
        MIMEText(
            html_content,
            "html",
            "utf-8"
        )
    )

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT
    ) as server:

        server.starttls()

        server.login(
            settings.SMTP_USERNAME,
            settings.SMTP_PASSWORD
        )

        server.sendmail(
            settings.MAIL_FROM,
            to_email,
            message.as_string()
        )

    return True