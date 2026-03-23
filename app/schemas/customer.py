"""Customer Pydantic schemas for request and response validation."""

from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    """Schema for creating a new customer."""

    name: str
    email: str
    phone: str | None = None
    address: str | None = None


class CustomerUpdate(BaseModel):
    """Schema for partially updating an existing customer."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class CustomerResponse(BaseModel):
    """Schema returned when reading a customer."""

    id: int
    name: str
    email: str
    phone: str | None = None
    address: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CountResponse(BaseModel):
    """Schema returned by the count endpoint."""

    count: int


class ErrorResponse(BaseModel):
    """Schema for error responses."""

    error: str
