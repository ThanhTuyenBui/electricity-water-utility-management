
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_consumption_report(
    db: Session,
    year: int = None,
    month: int = None,
    service_type: str = None
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_consumption_report(
                :p_year,
                :p_month,
                :p_service_type
            )
        """),
        {
            "p_year": year,
            "p_month": month,
            "p_service_type": service_type
        }
    )

    return [dict(row) for row in result.mappings().all()]


def get_revenue_report(
    db: Session,
    year: int = None,
    month: int = None,
    service_type: str = None
):
    result = db.execute(
        text("""
            SELECT *
            FROM public.get_revenue_report(
                :p_year,
                :p_month,
                :p_service_type
            )
        """),
        {
            "p_year": year,
            "p_month": month,
            "p_service_type": service_type
        }
    )

    return [dict(row) for row in result.mappings().all()]
