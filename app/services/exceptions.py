"""Exceções de domínio da camada de serviço."""


class ServiceError(Exception):
    """Exceção base para erros de negócio."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(ServiceError):
    """Recurso solicitado não encontrado."""


class DuplicateError(ServiceError):
    """Violação de unicidade (e.g. e-mail duplicado)."""


class ValidationError(ServiceError):
    """Dados de entrada inválidos."""
