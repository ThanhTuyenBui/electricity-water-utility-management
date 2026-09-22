from pydantic import BaseModel, Field
from typing import Optional


class EmployeeCreate(BaseModel):
    username: str = Field(
        min_length=4,
        max_length=50
    )

    password: str = Field(
        min_length=6,
        max_length=100
    )

    employee_code: str = Field(
        min_length=1,
        max_length=20
    )

    full_name: str = Field(
        min_length=1,
        max_length=100
    )

    phone: Optional[str] = Field(
        default=None,
        max_length=15
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

    phone: Optional[str] = Field(
        default=None,
        max_length=15
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
    phone: Optional[str]
    department: Optional[str]
    position: Optional[str]
    assigned_area: Optional[str]
    status: str

    class Config:
        from_attributes = True

class EmployeeSelfUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
