"""Customer model."""

from app import db


class Customer(db.Model):
    """Represents a customer of the store.

    Attributes:
        id (int): Primary key, auto-incremented unique identifier.
        name (str): Full name of the customer.
        email (str): Unique e-mail address of the customer.
        phone (str): Phone number of the customer.
        address (str): Mailing address of the customer.
    """

    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        """Serialize the customer instance to a dictionary.

        Returns:
            dict: Dictionary representation of the customer.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
        }
