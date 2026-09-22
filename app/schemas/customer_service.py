from pydantic import BaseModel, Field


class CounterRegisterRequest(BaseModel):
    username: str = Field(min_length=4, max_length=50)
    email: str
    password: str = Field(min_length=6, max_length=100)

    full_name: str = Field(min_length=1, max_length=100)
    phone: str | None = None
    identity_number: str | None = None
    address: str | None = None

    # 1 = Điện, 2 = Nước, [1, 2] = cả hai
    service_ids: list[int] = Field(min_length=1)


class CustomerServiceActionResponse(BaseModel):
    message: str
    user_id: int | None = None