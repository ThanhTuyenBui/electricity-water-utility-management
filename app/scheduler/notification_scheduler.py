
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import text
from zoneinfo import ZoneInfo

from app.core.database import SessionLocal


# Múi giờ Việt Nam
TIMEZONE = ZoneInfo("Asia/Ho_Chi_Minh")

# Khởi tạo Scheduler
scheduler = BackgroundScheduler(
    timezone=TIMEZONE
)


def send_daily_payment_reminders():
    """
    Tự động kiểm tra và tạo thông báo nhắc thanh toán.
    Chỉ xử lý các hóa đơn còn 3 ngày đến hạn.
    """

    db = SessionLocal()

    try:
        result = db.execute(
            text("""
                SELECT public.send_payment_reminders(
                    (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Ho_Chi_Minh')::DATE
                );
            """)
        )

        inserted_count = result.scalar()

        db.commit()

        print(
            f"[NOTIFICATION SCHEDULER] "
            f"Hoàn thành. Số thông báo được tạo: {inserted_count}"
        )

    except Exception as e:
        db.rollback()

        print(
            f"[NOTIFICATION SCHEDULER] "
            f"Lỗi khi tạo thông báo: {e}"
        )

    finally:
        db.close()


def start_scheduler():
    """
    Khởi động Scheduler chạy lúc 08:00 mỗi ngày.
    """

    if scheduler.running:
        return

    scheduler.add_job(
        send_daily_payment_reminders,
        trigger=CronTrigger(
            hour=8,
            minute=0,
            timezone=TIMEZONE
        ),
        id="daily_payment_reminders",
        name="Tự động nhắc thanh toán hóa đơn",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
        misfire_grace_time=3600
    )

    scheduler.start()

    print(
        "[NOTIFICATION SCHEDULER] "
        "Đã khởi động. Lịch chạy: 08:00 mỗi ngày."
    )
    print("[NOTIFICATION SCHEDULER] Công việc đã đăng ký:", scheduler.get_jobs())


def stop_scheduler():
    """
    Dừng Scheduler khi ứng dụng tắt.
    """

    if scheduler.running:
        scheduler.shutdown(wait=False)

        print(
            "[NOTIFICATION SCHEDULER] "
            "Đã dừng Scheduler."
        )
