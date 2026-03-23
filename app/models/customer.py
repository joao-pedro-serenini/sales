"""Modelo de cliente."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Customer(Base):
    """Representa um cliente da loja.

    Atributos:
        id: Chave primária, identificador único auto-incrementado.
        name: Nome completo do cliente.
        email: Endereço de e-mail único do cliente.
        phone: Número de telefone do cliente.
        address: Endereço postal do cliente.
    """

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    phone: Mapped[str | None] = mapped_column(String(20), default=None)
    address: Mapped[str | None] = mapped_column(String(255), default=None)
