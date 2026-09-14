from fastapi import FastAPI
from sqlalchemy import text
from app.database.database import engine
from app.routers import customers


app = FastAPI(
    title="Electric Water Management API",
    version="1.0.0"
)


app.include_router(
    customers.router,
    prefix="/api/customers",
    tags=["Customers"]
)

@app.get("/test-db")
def test_database():

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT version();")
        )

        version = result.fetchone()[0]

    return {
        "database": "PostgreSQL",
        "version": version
    }


@app.get("/")
def root():
    return {
        "message": "Electric Water Management API is running"
    }