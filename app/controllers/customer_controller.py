"""Customer controller — HTTP layer (FastAPI Router)."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.customer import (
    CountResponse,
    CustomerCreate,
    CustomerResponse,
    CustomerUpdate,
    ErrorResponse,
)
from app.services.customer_service import CustomerService

router = APIRouter(prefix="/customers", tags=["customers"])

DbSession = Annotated[Session, Depends(get_db)]


def _get_service(db: DbSession) -> CustomerService:
    """Dependency that provides a :class:`CustomerService` with a DB session."""
    return CustomerService(db)


ServiceDep = Annotated[CustomerService, Depends(_get_service)]


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


@router.post(
    "",
    status_code=201,
    response_model=CustomerResponse,
    responses={400: {"model": ErrorResponse}},
)
def create_customer(
    body: CustomerCreate,
    service: ServiceDep,
) -> CustomerResponse:
    """Create a new customer.

    ``name`` and ``email`` are required; ``phone`` and ``address`` are
    optional.
    """
    customer, error = service.create_customer(body)
    if error:
        raise HTTPException(status_code=400, detail=error)
    assert customer is not None
    return CustomerResponse.model_validate(customer)


# ---------------------------------------------------------------------------
# Read — collection
# ---------------------------------------------------------------------------


@router.get("", response_model=list[CustomerResponse])
def find_all(service: ServiceDep) -> list[CustomerResponse]:
    """Return all customers."""
    customers = service.get_all_customers()
    return [CustomerResponse.model_validate(c) for c in customers]


@router.get("/count", response_model=CountResponse)
def count(service: ServiceDep) -> CountResponse:
    """Return the total number of customers."""
    return CountResponse(count=service.count_customers())


@router.get("/name/{name}", response_model=list[CustomerResponse])
def find_by_name(name: str, service: ServiceDep) -> list[CustomerResponse]:
    """Return customers whose name contains *name* (case-insensitive)."""
    customers = service.get_customers_by_name(name)
    return [CustomerResponse.model_validate(c) for c in customers]


# ---------------------------------------------------------------------------
# Read — single item
# ---------------------------------------------------------------------------


@router.get(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={404: {"model": ErrorResponse}},
)
def find_by_id(customer_id: int, service: ServiceDep) -> CustomerResponse:
    """Return a single customer by ID."""
    customer = service.get_customer_by_id(customer_id)
    if customer is None:
        raise HTTPException(
            status_code=404,
            detail=f"Customer with id {customer_id} not found.",
        )
    return CustomerResponse.model_validate(customer)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


@router.put(
    "/{customer_id}",
    response_model=CustomerResponse,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def update_customer(
    customer_id: int,
    body: CustomerUpdate,
    service: ServiceDep,
) -> CustomerResponse:
    """Update an existing customer."""
    customer, error, status = service.update_customer(customer_id, body)
    if error:
        raise HTTPException(status_code=status, detail=error)
    assert customer is not None
    return CustomerResponse.model_validate(customer)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


@router.delete(
    "/{customer_id}",
    status_code=204,
    responses={404: {"model": ErrorResponse}},
)
def delete_customer(customer_id: int, service: ServiceDep) -> None:
    """Delete a customer by ID."""
    error, status = service.delete_customer(customer_id)
    if error:
        raise HTTPException(status_code=status, detail=error)
