"""Schemas Pydantic de cliente para validação de requisições e respostas."""

from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    """Schema para criação de um novo cliente."""

    name: str
    email: str
    phone: str | None = None
    address: str | None = None


class CustomerUpdate(BaseModel):
    """Schema para atualização parcial de um cliente existente."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    address: str | None = None


class CustomerResponse(BaseModel):
    """Schema retornado na leitura de um cliente."""

    id: int
    name: str
    email: str
    phone: str | None = None
    address: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CountResponse(BaseModel):
    """Schema retornado pelo endpoint de contagem."""

    count: int


class ErrorResponse(BaseModel):
    """Schema para respostas de erro."""

    error: str
