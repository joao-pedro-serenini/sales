"""Serviço de clientes — camada de lógica de negócio."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.exceptions import DuplicateError, NotFoundError, ValidationError


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

    def create_customer(self, data: CustomerCreate) -> Customer:
        """Valida ``data`` e persiste um novo cliente.

        Raises:
            ValidationError: Se campos obrigatórios estiverem vazios.
            DuplicateError: Se o e-mail já estiver cadastrado.
        """
        name = data.name.strip()
        email = data.email.strip()
        if not name:
            raise ValidationError("The 'name' field is required.")
        if not email:
            raise ValidationError("The 'email' field is required.")
        phone = data.phone.strip() if data.phone else None
        address = data.address.strip() if data.address else None
        try:
            return self._repo.create(
                name=name, email=email, phone=phone, address=address
            )
        except IntegrityError:
            raise DuplicateError(f"A customer with e-mail '{email}' already exists.")

    def update_customer(self, customer_id: int, data: CustomerUpdate) -> Customer:
        """Atualiza um cliente existente com os campos presentes em ``data``.

        Raises:
            NotFoundError: Se o cliente não for encontrado.
            ValidationError: Se campos obrigatórios ficarem vazios após strip.
            DuplicateError: Se o e-mail já estiver cadastrado por outro cliente.
        """
        customer = self._repo.find_by_id(customer_id)
        if customer is None:
            raise NotFoundError(f"Customer with id {customer_id} not found.")
        name = data.name
        email = data.email
        phone = data.phone
        address = data.address
        if name is not None:
            name = name.strip() if name else None
            if not name:
                raise ValidationError("The 'name' field cannot be empty.")
        if email is not None:
            email = email.strip() if email else None
            if not email:
                raise ValidationError("The 'email' field cannot be empty.")
        if phone is not None:
            phone = phone.strip() or None
        if address is not None:
            address = address.strip() or None
        try:
            return self._repo.update(
                customer, name=name, email=email, phone=phone, address=address
            )
        except IntegrityError:
            raise DuplicateError(f"A customer with e-mail '{email}' already exists.")

    def delete_customer(self, customer_id: int) -> None:
        """Exclui um cliente pela chave primária.

        Raises:
            NotFoundError: Se o cliente não for encontrado.
        """
        customer = self._repo.find_by_id(customer_id)
        if customer is None:
            raise NotFoundError(f"Customer with id {customer_id} not found.")
        self._repo.delete(customer)

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
