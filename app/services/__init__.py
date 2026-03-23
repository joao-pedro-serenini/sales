"""Pacote de serviços."""

from app.services.customer_service import CustomerService
from app.services.exceptions import DuplicateError, NotFoundError, ValidationError

__all__ = [
    "CustomerService",
    "DuplicateError",
    "NotFoundError",
    "ValidationError",
]
