"""Customer repository — data-access layer."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    """Handles all direct database interactions for the Customer model.

    This layer abstracts SQLAlchemy queries so that the Service layer
    never needs to import the session or write raw ORM queries.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        name: str,
        email: str,
        phone: str | None = None,
        address: str | None = None,
    ) -> Customer:
        """Persist a new customer record.

        Args:
            name: Full name of the customer.
            email: Unique e-mail address.
            phone: Optional phone number.
            address: Optional mailing address.

        Returns:
            The newly created :class:`Customer` instance.
        """
        customer = Customer(name=name, email=email, phone=phone, address=address)
        self._session.add(customer)
        self._session.commit()
        self._session.refresh(customer)
        return customer

    def find_all(self) -> list[Customer]:
        """Return all customer records."""
        return list(self._session.execute(select(Customer)).scalars().all())

    def find_by_id(self, customer_id: int) -> Customer | None:
        """Return a single customer by primary key."""
        return self._session.get(Customer, customer_id)

    def find_by_name(self, name: str) -> list[Customer]:
        """Return customers whose name contains the given string (case-insensitive)."""
        stmt = select(Customer).where(Customer.name.ilike(f"%{name}%"))
        return list(self._session.execute(stmt).scalars().all())

    def count(self) -> int:
        """Return the total number of customer records."""
        result = self._session.execute(select(func.count(Customer.id))).scalar()
        return result if result is not None else 0

    def update(
        self,
        customer: Customer,
        name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        address: str | None = None,
    ) -> Customer:
        """Apply partial updates to an existing customer record.

        Only fields that are explicitly provided (not ``None``) are updated.
        """
        if name is not None:
            customer.name = name
        if email is not None:
            customer.email = email
        if phone is not None:
            customer.phone = phone
        if address is not None:
            customer.address = address
        self._session.commit()
        self._session.refresh(customer)
        return customer

    def delete(self, customer: Customer) -> None:
        """Delete a customer record from the database."""
        self._session.delete(customer)
        self._session.commit()
