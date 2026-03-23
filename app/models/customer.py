"""Customer model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Customer(Base):
    """Represents a customer of the store.

    Attributes:
        id: Primary key, auto-incremented unique identifier.
        name: Full name of the customer.
        email: Unique e-mail address of the customer.
        phone: Phone number of the customer.
        address: Mailing address of the customer.
    """

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), default=None)
    address: Mapped[str | None] = mapped_column(String(255), default=None)
