from datetime import date

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.repositories.tariff import (
    get_tariffs as get_tariffs_repo,
    get_tariff_detail as get_tariff_detail_repo,
    create_tariff as create_tariff_repo,
    create_tariff_version as create_tariff_version_repo,
    update_tariff as update_tariff_repo
)


# ============================================================
# XỬ LÝ LỖI DATABASE
# ============================================================

def handle_database_error(db: Session, exc: Exception):

    db.rollback()

    original = getattr(exc, "orig", None)

    sqlstate = (
        getattr(original, "sqlstate", None)
        or getattr(original, "pgcode", None)
    )

    if sqlstate == "P0001":

        message = getattr(
            getattr(original, "diag", None),
            "message_primary",
            "Dữ liệu không hợp lệ"
        )

        if "Không tìm thấy biểu giá" in message:
            raise HTTPException(
                status_code=404,
                detail=message
            ) from exc

        raise HTTPException(
            status_code=400,
            detail=message
        ) from exc

    raise HTTPException(
        status_code=500,
        detail="Đã xảy ra lỗi khi xử lý biểu giá"
    ) from exc


# ============================================================
# 1. LẤY DANH SÁCH BIỂU GIÁ
# ============================================================

def get_tariffs(
    db: Session,
    role_id: int
):

    try:
        data = get_tariffs_repo(db=db)

        # Admin và nhân viên được xem tất cả biểu giá.
        if role_id in (1, 2):
            return data

        # Khách hàng chỉ được xem biểu giá đang áp dụng.
        if role_id == 3:
            return [
                item for item in data
                if item["tariff_status"] == "ACTIVE"
            ]

        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền xem biểu giá"
        )

    except HTTPException:
        raise

    except SQLAlchemyError as exc:
        handle_database_error(db, exc)


# ============================================================
# 2. LẤY CHI TIẾT BIỂU GIÁ
# ============================================================


def get_tariff_detail(db: Session, tariff_id: int, role_id: int):
    try:
        rows = get_tariff_detail_repo(
            db=db,
            tariff_id=tariff_id
        )

        if not rows:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy biểu giá"
            )

        tariff = {
            "tariff_id": rows[0]["tariff_id"],
            "service_id": rows[0]["service_id"],
            "service_name": rows[0]["service_name"],
            "effective_from": rows[0]["effective_from"],
            "effective_to": rows[0]["effective_to"],
            "created_at": rows[0]["created_at"],
            "vat_percent": rows[0]["vat_percent"],
            "environment_fee_percent": rows[0]["environment_fee_percent"],
            "tiers": []
        }

        # Gom các bậc giá vào mảng tiers
        for row in rows:
            if row["tier_id"] is not None:
                tariff["tiers"].append({
                    "tier_id": row["tier_id"],
                    "from_value": row["from_value"],
                    "to_value": row["to_value"],
                    "unit_price": row["unit_price"]
                })

        # Khách hàng chỉ được xem biểu giá đang áp dụng
        if role_id == 3:
            today = date.today()

            is_active = (
                tariff["effective_from"] <= today
                and (
                    tariff["effective_to"] is None
                    or tariff["effective_to"] >= today
                )
            )

            if not is_active:
                raise HTTPException(
                    status_code=404,
                    detail="Không tìm thấy biểu giá đang áp dụng"
                )

        elif role_id not in (1, 2):
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền xem biểu giá"
            )

        return tariff

    except HTTPException:
        raise

    except SQLAlchemyError as exc:
        handle_database_error(db, exc)



# ============================================================
# 3. TẠO BIỂU GIÁ
# ============================================================

def create_tariff(
    db: Session,
    data: dict
):

    try:
        tariff_id = create_tariff_repo(
            db=db,
            service_id=data["service_id"],
            effective_from=data["effective_from"],
            tiers=data["tiers"],
            vat_percent=data.get("vat_percent"),
            environment_fee_percent=data.get(
                "environment_fee_percent"
            )
        )

        return {
            "message": "Tạo biểu giá thành công",
            "tariff_id": tariff_id
        }

    except SQLAlchemyError as exc:
        handle_database_error(db, exc)


# ============================================================
# 4. TẠO PHIÊN BẢN BIỂU GIÁ
# ============================================================

def create_tariff_version(
    db: Session,
    tariff_id: int,
    data: dict
):

    try:
        new_tariff_id = create_tariff_version_repo(
            db=db,
            source_tariff_id=tariff_id,
            effective_from=data["effective_from"],
            vat_percent=data.get("vat_percent"),
            environment_fee_percent=data.get(
                "environment_fee_percent"
            ),
            tiers=data.get("tiers")
        )

        return {
            "message": "Tạo phiên bản biểu giá thành công",
            "tariff_id": new_tariff_id
        }

    except SQLAlchemyError as exc:
        handle_database_error(db, exc)


# ============================================================
# 5. CẬP NHẬT BIỂU GIÁ
# ============================================================

def update_tariff(
    db: Session,
    tariff_id: int,
    data: dict
):

    try:
        result = update_tariff_repo(
            db=db,
            tariff_id=tariff_id,
            tiers=data["tiers"],
            vat_percent=data.get("vat_percent"),
            environment_fee_percent=data.get(
                "environment_fee_percent"
            )
        )

        return {
            "message": "Cập nhật biểu giá thành công",
            "result": result
        }

    except SQLAlchemyError as exc:
        handle_database_error(db, exc)