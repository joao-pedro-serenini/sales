"""Customer service — business logic layer."""

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """Encapsulates the business rules for the Customer resource.

    The service delegates all persistence operations to
    :class:`~app.repositories.customer_repository.CustomerRepository`
    and applies validation / transformation logic before and after.
    """

    def __init__(self, session: Session) -> None:
        self._repo = CustomerRepository(session)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_customer(
        self, data: CustomerCreate
    ) -> tuple[Customer | None, str | None]:
        """Validate ``data`` and persist a new customer.

        Returns:
            A ``(customer, error)`` tuple.  On success ``error`` is
            ``None``; on failure ``customer`` is ``None``.
        """
        name = data.name.strip()
        email = data.email.strip()
        if not name:
            return None, "The 'name' field is required."
        if not email:
            return None, "The 'email' field is required."
        phone = data.phone.strip() if data.phone else None
        address = data.address.strip() if data.address else None
        try:
            customer = self._repo.create(
                name=name, email=email, phone=phone, address=address
            )
        except Exception:
            return None, f"A customer with e-mail '{email}' already exists."
        return customer, None

    def update_customer(
        self, customer_id: int, data: CustomerUpdate
    ) -> tuple[Customer | None, str | None, int]:
        """Update an existing customer with the fields present in ``data``.

        Returns:
            A ``(customer, error, status_code)`` tuple.
        """
        customer = self._repo.find_by_id(customer_id)
        if customer is None:
            return None, f"Customer with id {customer_id} not found.", 404
        name = data.name
        email = data.email
        phone = data.phone
        address = data.address
        if name is not None:
            name = name.strip() or None
        if email is not None:
            email = email.strip() or None
        try:
            customer = self._repo.update(
                customer, name=name, email=email, phone=phone, address=address
            )
        except Exception:
            return None, f"A customer with e-mail '{email}' already exists.", 400
        return customer, None, 200

    def delete_customer(self, customer_id: int) -> tuple[str | None, int]:
        """Delete a customer by primary key.

        Returns:
            A ``(error, status_code)`` tuple.
        """
        customer = self._repo.find_by_id(customer_id)
        if customer is None:
            return f"Customer with id {customer_id} not found.", 404
        self._repo.delete(customer)
        return None, 204

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get_all_customers(self) -> list[Customer]:
        """Return all customers."""
        return self._repo.find_all()

    def get_customer_by_id(self, customer_id: int) -> Customer | None:
        """Return a single customer by primary key."""
        return self._repo.find_by_id(customer_id)

    def get_customers_by_name(self, name: str) -> list[Customer]:
        """Return customers whose name contains ``name`` (case-insensitive)."""
        return self._repo.find_by_name(name)

    def count_customers(self) -> int:
        """Return the total number of customer records."""
        return self._repo.count()
