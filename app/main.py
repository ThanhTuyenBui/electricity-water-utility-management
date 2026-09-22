from fastapi import FastAPI
from sqlalchemy import text

from app.database.database import engine

from app.routers import auth
from app.routers import employees
from app.routers import customers
from app.routers import customer_service

import uvicorn
from app.core.config import settings


app = FastAPI(
    title="Electric Water Management API",
    version="1.0.0"
)


app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"]
)


app.include_router(
    employees.router,
    prefix="/api/employees",
    tags=["Employees"]
)


app.include_router(
    customers.router,
    prefix="/api/customers",
    tags=["Customers"]
)


app.include_router(
    customer_service.router,
    prefix="/api"
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


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )