import json

from sqlalchemy import text
from sqlalchemy.orm import Session


# ============================================================
# 1. LẤY DANH SÁCH BIỂU GIÁ
# ============================================================

def get_tariffs(db: Session):
    result = db.execute(
        text("""
            SELECT *
            FROM get_tariffs()
            ORDER BY effective_from DESC
        """)
    )

    return result.mappings().all()


# ============================================================
# 2. LẤY CHI TIẾT BIỂU GIÁ
# ============================================================

def get_tariff_detail(
    db: Session,
    tariff_id: int
):
    result = db.execute(
        text("""
            SELECT *
            FROM get_tariff_detail(:tariff_id)
        """),
        {
            "tariff_id": tariff_id
        }
    )

    return result.mappings().all()


# ============================================================
# 3. TẠO BIỂU GIÁ
# ============================================================

def create_tariff(
    db: Session,
    service_id: int,
    effective_from,
    tiers: list[dict],
    vat_percent=None,
    environment_fee_percent=None
):
    query = text("""
        SELECT create_tariff(
            :service_id,
            :effective_from,
            CAST(:tiers AS JSONB),
            :vat_percent,
            :environment_fee_percent
        )
    """)

    result = db.execute(
        query,
        {
            "service_id": service_id,
            "effective_from": effective_from,
            "tiers": json.dumps(tiers),
            "vat_percent": vat_percent,
            "environment_fee_percent": environment_fee_percent
        }
    )

    tariff_id = result.scalar_one()

    db.commit()

    return tariff_id


# ============================================================
# 4. TẠO PHIÊN BẢN BIỂU GIÁ
# ============================================================

def create_tariff_version(
    db: Session,
    source_tariff_id: int,
    effective_from,
    vat_percent=None,
    environment_fee_percent=None,
    tiers: list[dict] | None = None
):
    query = text("""
        SELECT create_tariff_version(
            :source_tariff_id,
            :effective_from,
            :vat_percent,
            :environment_fee_percent,
            CAST(:tiers AS JSONB)
        )
    """)

    params = {
        "source_tariff_id": source_tariff_id,
        "effective_from": effective_from,
        "vat_percent": vat_percent,
        "environment_fee_percent": environment_fee_percent,
        "tiers": json.dumps(tiers) if tiers is not None else None
    }

    result = db.execute(query, params)

    tariff_id = result.scalar_one()

    db.commit()

    return tariff_id


# ============================================================
# 5. CẬP NHẬT BIỂU GIÁ
# ============================================================

def update_tariff(
    db: Session,
    tariff_id: int,
    tiers: list[dict],
    vat_percent=None,
    environment_fee_percent=None
):
    query = text("""
        SELECT update_tariff(
            :tariff_id,
            CAST(:tiers AS JSONB),
            :vat_percent,
            :environment_fee_percent
        )
    """)

    result = db.execute(
        query,
        {
            "tariff_id": tariff_id,
            "tiers": json.dumps(tiers),
            "vat_percent": vat_percent,
            "environment_fee_percent": environment_fee_percent
        }
    )

    updated = result.scalar_one()

    db.commit()

    return updated