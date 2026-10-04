from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class EmployeeCreate(BaseModel):
    username: str = Field(
        min_length=4,
        max_length=50
    )

    employee_code: str = Field(
        min_length=1,
        max_length=20
    )

    full_name: str = Field(
        min_length=1,
        max_length=100
    )

    email: EmailStr

    phone: str = Field(
        min_length=10,
        max_length=10
    )

    department: Optional[str] = Field(
        default=None,
        max_length=100
    )

    position: Optional[str] = Field(
        default=None,
        max_length=100
    )

    assigned_area: Optional[str] = Field(
        default=None,
        max_length=100
    )


class EmployeeUpdate(BaseModel):
    full_name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    email: Optional[EmailStr] = None

    phone: Optional[str] = Field(
        default=None,
        min_length=10,
        max_length=10
    )

    department: Optional[str] = Field(
        default=None,
        max_length=100
    )

    position: Optional[str] = Field(
        default=None,
        max_length=100
    )

    assigned_area: Optional[str] = Field(
        default=None,
        max_length=100
    )

    status: Optional[str] = Field(
        default=None,
        max_length=20
    )


class EmployeeStatusUpdate(BaseModel):
    status: str


class EmployeeResponse(BaseModel):
    employee_id: int
    user_id: int
    employee_code: str
    full_name: str
    email: Optional[str]
    phone: Optional[str]
    department: Optional[str]
    position: Optional[str]
    assigned_area: Optional[str]
    status: str

    class Config:
        from_attributes = True


class EmployeeSelfUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
