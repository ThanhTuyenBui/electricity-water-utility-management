from app.providers.sms.fake_sms import FakeSMSProvider


class SMSService:

    def __init__(self):
        self.provider = FakeSMSProvider()

    def send_customer_password(
        self,
        phone_number: str,
        username: str,
        password: str
    ):
        message = (
            "Đơn vị điện nước thông báo:\n"
            "Tài khoản của quý khách đã được tạo.\n\n"
            f"Tên đăng nhập: {username}\n"
            f"Mật khẩu tạm thời: {password}\n\n"
            "Vui lòng đăng nhập và đổi mật khẩu sau lần đầu sử dụng."
        )

        return self.provider.send_sms(
            phone_number,
            message
        )