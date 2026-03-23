"""Repositório de clientes — camada de acesso a dados."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.customer import Customer


class CustomerRepository:
    """Gerencia todas as interações diretas com o banco de dados para o modelo Customer.

    Esta camada abstrai as consultas SQLAlchemy para que a camada de Service
    nunca precise importar a sessão ou escrever consultas ORM diretamente.
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
        """Persiste um novo registro de cliente.

        Args:
            name: Nome completo do cliente.
            email: Endereço de e-mail único.
            phone: Número de telefone (opcional).
            address: Endereço postal (opcional).

        Retorna:
            A instância de :class:`Customer` recém-criada.
        """
        customer = Customer(name=name, email=email, phone=phone, address=address)
        self._session.add(customer)
        self._session.commit()
        self._session.refresh(customer)
        return customer

    def find_all(self) -> list[Customer]:
        """Retorna todos os registros de clientes."""
        return list(self._session.execute(select(Customer)).scalars().all())

    def find_by_id(self, customer_id: int) -> Customer | None:
        """Retorna um único cliente pela chave primária."""
        return self._session.get(Customer, customer_id)

    def find_by_name(self, name: str) -> list[Customer]:
        """Retorna clientes cujo nome contém a string fornecida (sem distinção de maiúsculas/minúsculas)."""
        stmt = select(Customer).where(Customer.name.ilike(f"%{name}%"))
        return list(self._session.execute(stmt).scalars().all())

    def count(self) -> int:
        """Retorna o número total de registros de clientes."""
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
        """Aplica atualizações parciais a um registro de cliente existente.

        Apenas campos fornecidos explicitamente (não ``None``) são atualizados.
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
        """Exclui um registro de cliente do banco de dados."""
        self._session.delete(customer)
        self._session.commit()
