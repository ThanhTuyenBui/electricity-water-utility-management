from sqlalchemy import text
from sqlalchemy.orm import Session


# =========================================================
# 1. KHÁCH HÀNG XEM THÔNG TIN CỦA MÌNH
# =========================================================

def get_my_customer(
    db: Session,
    user_id: int
):

    result = db.execute(
        text("""
            SELECT
                c.customer_id,
                c.user_id,
                c.full_name,
                c.phone,
                c.identity_number,
                c.address,
                u.status
            FROM customers c
            JOIN users u
                ON u.user_id = c.user_id
            WHERE c.user_id = :user_id
        """),
        {
            "user_id": user_id
        }
    )

    return result.mappings().first()


# =========================================================
# 2. KHÁCH HÀNG SỬA THÔNG TIN
# =========================================================

def update_customer_self(
    db: Session,
    user_id: int,
    full_name: str | None,
    phone: str | None,
    identity_number: str | None
):

    db.execute(
        text("""
            CALL update_customer_self(
                :user_id,
                :full_name,
                :phone,
                :identity_number
            )
        """),
        {
            "user_id": user_id,
            "full_name": full_name,
            "phone": phone,
            "identity_number": identity_number
        }
    )


# =========================================================
# 3. DANH SÁCH KHÁCH HÀNG
# =========================================================

def get_customers(
    db: Session,
    page: int,
    page_size: int,
    search: str | None,
    area: str | None,
    sort_by: str,
    sort_order: str
):

    offset = (page - 1) * page_size

    allowed_sort_columns = {
        "customer_id": "c.customer_id",
        "full_name": "c.full_name",
        "phone": "c.phone",
        "identity_number": "c.identity_number",
        "address": "c.address",
        "status": "u.status"
    }

    sort_column = allowed_sort_columns.get(
        sort_by,
        "c.customer_id"
    )

    sort_direction = (
        "DESC"
        if sort_order.upper() == "DESC"
        else "ASC"
    )

    query = text(f"""
        SELECT
            c.customer_id,
            c.user_id,
            c.full_name,
            c.phone,
            c.identity_number,
            c.address,
            u.status,

            COUNT(*) OVER() AS total_count

        FROM customers c

        JOIN users u
            ON u.user_id = c.user_id

        WHERE
            (
                :search IS NULL
                OR c.full_name ILIKE :search_pattern
                OR c.phone ILIKE :search_pattern
                OR c.identity_number ILIKE :search_pattern
            )

        AND
            (
                :area IS NULL
                OR c.address ILIKE :area_pattern
            )

        ORDER BY {sort_column} {sort_direction}

        LIMIT :page_size
        OFFSET :offset
    """)

    result = db.execute(
        query,
        {
            "search": search,

            "search_pattern": (
                f"%{search}%"
                if search
                else "%"
            ),

            "area": area,

            "area_pattern": (
                f"%{area}%"
                if area
                else "%"
            ),

            "page_size": page_size,
            "offset": offset
        }
    )

    return result.mappings().all()


# =========================================================
# 4. KHÓA / MỞ KHÁCH HÀNG
# =========================================================

def change_customer_status(
    db: Session,
    customer_id: int,
    customer_status: str
):

    result = db.execute(
        text("""
            CALL change_customer_status(
                :customer_id,
                :customer_status
            )
        """),
        {
            "customer_id": customer_id,
            "customer_status": customer_status
        }
    )

    return result