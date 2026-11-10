
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# =====================================================
# 1. SCHEMA THÔNG TIN THÔNG BÁO
# Dùng cho danh sách và chi tiết thông báo
# =====================================================

class NotificationResponse(BaseModel):
    notification_id: int
    customer_id: int
    customer_code: str
    customer_name: str

    bill_id: Optional[int] = None
    bill_code: Optional[str] = None

    notification_type: str
    channel: str

    title: Optional[str] = None
    content: str
    phone_number: Optional[str] = None

    status: str
    retry_count: int
    error_message: Optional[str] = None

    created_at: datetime
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None


# =====================================================
# 2. SCHEMA DANH SÁCH THÔNG BÁO
# =====================================================

class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total_records: int


# =====================================================
# 3. SCHEMA KẾT QUẢ GỬI LẠI THÔNG BÁO
# =====================================================

class NotificationRetryResponse(BaseModel):
    notification_id: int
    channel: str
    status: str
    retry_count: int
    error_message: Optional[str] = None
    message: str


# =====================================================
# 4. SCHEMA DANH SÁCH THÔNG BÁO THẤT BẠI
# =====================================================

class FailedNotificationResponse(BaseModel):
    notification_id: int
    customer_id: int
    customer_code: str
    customer_name: str

    bill_id: Optional[int] = None
    bill_code: Optional[str] = None

    notification_type: str
    channel: str

    title: Optional[str] = None
    content: str
    phone_number: Optional[str] = None

    retry_count: int
    error_message: Optional[str] = None
    created_at: datetime


class FailedNotificationListResponse(BaseModel):
    items: list[FailedNotificationResponse]
    total_records: int
