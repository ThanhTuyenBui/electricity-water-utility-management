from datetime import datetime
import os


class FakeSMSProvider:

    def send_sms(self, phone_number: str, message: str):

        if os.getenv("APP_ENV", "development") == "development":
            print("\n==============================")
            print("        MOCK SMS - TEST")
            print("==============================")
            print(f"To      : {phone_number}")
            print(f"Message : {message}")
            print("==============================\n")
        else:
            print("[MOCK SMS] SMS request processed.")

        return {
            "phone_number": phone_number,
            "message": message,
            "provider": "FAKE",
            "status": "SENT",
            "sent_at": datetime.now()
        }