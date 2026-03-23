"""Serviço de clientes — camada de lógica de negócio."""

from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CustomerService:
    """Encapsula as regras de negócio do recurso Customer.

    O serviço delega todas as operações de persistência ao
    :class:`~app.repositories.customer_repository.CustomerRepository`
    e aplica lógica de validação/transformação antes e depois.
    """

    def __init__(self, session: Session) -> None:
        self._repo = CustomerRepository(session)

    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create_customer(
        self, data: CustomerCreate
    ) -> tuple[Customer | None, str | None]:
        """Valida ``data`` e persiste um novo cliente.

        Retorna:
            Uma tupla ``(customer, error)``. Em caso de sucesso, ``error``
            é ``None``; em caso de falha, ``customer`` é ``None``.
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
        """Atualiza um cliente existente com os campos presentes em ``data``.

        Retorna:
            Uma tupla ``(customer, error, status_code)``.
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
        """Exclui um cliente pela chave primária.

        Retorna:
            Uma tupla ``(error, status_code)``.
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
        """Retorna todos os clientes."""
        return self._repo.find_all()

    def get_customer_by_id(self, customer_id: int) -> Customer | None:
        """Retorna um único cliente pela chave primária."""
        return self._repo.find_by_id(customer_id)

    def get_customers_by_name(self, name: str) -> list[Customer]:
        """Retorna clientes cujo nome contém ``name`` (sem distinção de maiúsculas/minúsculas)."""
        return self._repo.find_by_name(name)

    def count_customers(self) -> int:
        """Retorna o número total de registros de clientes."""
        return self._repo.count()
