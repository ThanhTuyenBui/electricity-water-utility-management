from datetime import datetime


class FakeSMSProvider:

    def send_sms(self, phone_number: str, message: str):

        print("\n==============================")
        print("        MOCK SMS")
        print("==============================")
        print(f"To      : {phone_number}")
        print(f"Message : {message}")
        print("==============================\n")

        return {
            "phone_number": phone_number,
            "message": message,
            "provider": "FAKE",
            "status": "SENT",
            "sent_at": datetime.now()
        }