from fastapi import FastAPI
from sqlalchemy import text
from contextlib import asynccontextmanager
from app.scheduler.notification_scheduler import start_scheduler, stop_scheduler
from app.database.database import engine

from app.routers import auth
from app.routers import employees
from app.routers import customer
from app.routers import customer_service
from app.routers import meter
from app.routers import tariff
from app.routers import bill
import uvicorn
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(
    title="Electric Water Management API",
    version="1.0.0",
    lifespan=lifespan
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
    customer.router,
    prefix="/api/customers",
    tags=["Customers"]
)


app.include_router(
    customer_service.router,
    prefix="/api",
    tags=["Customer Services"]
)


app.include_router(
    meter.router,
    prefix="/api",
    tags=["Meters"]
)

app.include_router(
    meter.reading_router,
    prefix="/api",
    tags=["Meter Readings"]
)


app.include_router(
    tariff.router,
    prefix="/api",
    tags=["Tariff Management"]
)

app.include_router(
    bill.router,
    prefix="/api/bills",
    tags=["Bill Management"]
)


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
