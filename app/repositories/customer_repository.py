"""Customer repository — data-access layer."""

from app import db
from app.models.customer import Customer


class CustomerRepository:
    """Handles all direct database interactions for the Customer model.

    This layer abstracts SQLAlchemy queries so that the Service layer
    never needs to import ``db`` or write raw ORM queries.
    """

    def create(self, name: str, email: str, phone: str = None, address: str = None) -> Customer:
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
        db.session.add(customer)
        db.session.commit()
        return customer

    def find_all(self) -> list[Customer]:
        """Return all customer records.

        Returns:
            List of all :class:`Customer` instances.
        """
        return db.session.execute(db.select(Customer)).scalars().all()

    def find_by_id(self, customer_id: int) -> Customer | None:
        """Return a single customer by primary key.

        Args:
            customer_id: The integer primary key to look up.

        Returns:
            The matching :class:`Customer` or ``None``.
        """
        return db.session.get(Customer, customer_id)

    def find_by_name(self, name: str) -> list[Customer]:
        """Return customers whose name contains the given string (case-insensitive).

        Args:
            name: Substring to search for in customer names.

        Returns:
            List of matching :class:`Customer` instances.
        """
        return (
            db.session.execute(
                db.select(Customer).where(Customer.name.ilike(f"%{name}%"))
            )
            .scalars()
            .all()
        )

    def count(self) -> int:
        """Return the total number of customer records.

        Returns:
            Integer count of all customers.
        """
        return db.session.execute(db.select(db.func.count(Customer.id))).scalar()

    def update(
        self,
        customer: Customer,
        name: str = None,
        email: str = None,
        phone: str = None,
        address: str = None,
    ) -> Customer:
        """Apply partial updates to an existing customer record.

        Only fields that are explicitly provided (not ``None``) are updated.

        Args:
            customer: The :class:`Customer` instance to update.
            name: New name value, if provided.
            email: New e-mail value, if provided.
            phone: New phone value, if provided.
            address: New address value, if provided.

        Returns:
            The updated :class:`Customer` instance.
        """
        if name is not None:
            customer.name = name
        if email is not None:
            customer.email = email
        if phone is not None:
            customer.phone = phone
        if address is not None:
            customer.address = address
        db.session.commit()
        return customer

    def delete(self, customer: Customer) -> None:
        """Delete a customer record from the database.

        Args:
            customer: The :class:`Customer` instance to remove.
        """
        db.session.delete(customer)
        db.session.commit()
