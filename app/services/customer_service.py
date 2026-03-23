"""Customer service — business logic layer."""

from app.repositories.customer_repository import CustomerRepository
from app.models.customer import Customer


class CustomerService:
    """Encapsulates the business rules for the Customer resource.

    The service delegates all persistence operations to
    :class:`~app.repositories.customer_repository.CustomerRepository`
    and applies validation / transformation logic before and after.
    """

    def __init__(self):
        self._repo = CustomerRepository()

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_customer(self, data: dict) -> tuple[Customer | None, str | None]:
        """Validate ``data`` and persist a new customer.

        Args:
            data: Dictionary that must contain at least ``name`` and
                ``email`` keys.

        Returns:
            A ``(customer, error)`` tuple.  On success ``error`` is
            ``None``; on failure ``customer`` is ``None`` and ``error``
            is a human-readable message string.
        """
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        if not name:
            return None, "The 'name' field is required."
        if not email:
            return None, "The 'email' field is required."
        phone = (data.get("phone") or "").strip() or None
        address = (data.get("address") or "").strip() or None
        try:
            customer = self._repo.create(name=name, email=email, phone=phone, address=address)
        except Exception:
            return None, f"A customer with e-mail '{email}' already exists."
        return customer, None

    def update_customer(
        self, customer_id: int, data: dict
    ) -> tuple[Customer | None, str | None, int]:
        """Update an existing customer with the fields present in ``data``.

        Args:
            customer_id: Primary key of the customer to update.
            data: Dictionary with optional ``name``, ``email``, ``phone``
                and/or ``address`` keys.

        Returns:
            A ``(customer, error, status_code)`` tuple.  On success
            ``error`` is ``None`` and ``status_code`` is ``200``; on
            failure ``customer`` is ``None``.
        """
        customer = self._repo.find_by_id(customer_id)
        if customer is None:
            return None, f"Customer with id {customer_id} not found.", 404
        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone")
        address = data.get("address")
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

        Args:
            customer_id: Primary key of the customer to delete.

        Returns:
            A ``(error, status_code)`` tuple.  On success ``error`` is
            ``None`` and ``status_code`` is ``204``.
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
        """Return all customers.

        Returns:
            List of :class:`~app.models.customer.Customer` instances.
        """
        return self._repo.find_all()

    def get_customer_by_id(self, customer_id: int) -> Customer | None:
        """Return a single customer by primary key.

        Args:
            customer_id: Primary key to look up.

        Returns:
            The matching customer or ``None``.
        """
        return self._repo.find_by_id(customer_id)

    def get_customers_by_name(self, name: str) -> list[Customer]:
        """Return customers whose name contains ``name`` (case-insensitive).

        Args:
            name: Substring to search for.

        Returns:
            List of matching customers.
        """
        return self._repo.find_by_name(name)

    def count_customers(self) -> int:
        """Return the total number of customer records.

        Returns:
            Integer count.
        """
        return self._repo.count()
