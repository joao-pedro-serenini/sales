"""Testes para os endpoints da API de clientes."""

from collections.abc import Generator

import httpx
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app import create_app
from app.database import Base, get_db

_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def _override_get_db() -> Generator[Session, None, None]:
    db = _TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def app() -> Generator[FastAPI, None, None]:
    """Cria uma aplicação FastAPI de teste com banco de dados SQLite em memória."""
    Base.metadata.create_all(bind=_engine)
    application = create_app()
    application.dependency_overrides[get_db] = _override_get_db
    yield application
    application.dependency_overrides.clear()
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    """Retorna um cliente de teste para a aplicação."""
    return TestClient(app)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _create(client: TestClient, **kwargs: str) -> httpx.Response:
    payload: dict[str, str] = {"name": "Test User", "email": "test@example.com"}
    payload.update(kwargs)
    return client.post("/customers", json=payload)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------


class TestCreateCustomer:
    def test_create_returns_201(self, client: TestClient) -> None:
        resp = _create(client)
        assert resp.status_code == 201

    def test_create_returns_customer_data(self, client: TestClient) -> None:
        resp = _create(client, name="Alice", email="alice@example.com")
        data = resp.json()
        assert data["name"] == "Alice"
        assert data["email"] == "alice@example.com"
        assert data["id"] is not None

    def test_create_missing_name_returns_422(self, client: TestClient) -> None:
        resp = client.post("/customers", json={"email": "a@b.com"})
        assert resp.status_code == 422

    def test_create_missing_email_returns_422(self, client: TestClient) -> None:
        resp = client.post("/customers", json={"name": "Bob"})
        assert resp.status_code == 422

    def test_create_duplicate_email_returns_400(self, client: TestClient) -> None:
        _create(client, email="dup@example.com")
        resp = _create(client, email="dup@example.com")
        assert resp.status_code == 400

    def test_create_with_optional_fields(self, client: TestClient) -> None:
        resp = client.post(
            "/customers",
            json={
                "name": "Carol",
                "email": "carol@example.com",
                "phone": "11999990000",
                "address": "Rua das Flores, 1",
            },
        )
        data = resp.json()
        assert data["phone"] == "11999990000"
        assert data["address"] == "Rua das Flores, 1"


# ---------------------------------------------------------------------------
# Find All
# ---------------------------------------------------------------------------


class TestFindAll:
    def test_empty_returns_empty_list(self, client: TestClient) -> None:
        resp = client.get("/customers")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_all_customers(self, client: TestClient) -> None:
        _create(client, name="A", email="a@a.com")
        _create(client, name="B", email="b@b.com")
        resp = client.get("/customers")
        assert resp.status_code == 200
        assert len(resp.json()) == 2


# ---------------------------------------------------------------------------
# Count
# ---------------------------------------------------------------------------


class TestCount:
    def test_count_zero(self, client: TestClient) -> None:
        resp = client.get("/customers/count")
        assert resp.status_code == 200
        assert resp.json() == {"count": 0}

    def test_count_after_creates(self, client: TestClient) -> None:
        _create(client, email="x1@x.com")
        _create(client, email="x2@x.com")
        resp = client.get("/customers/count")
        assert resp.json() == {"count": 2}


# ---------------------------------------------------------------------------
# Find By ID
# ---------------------------------------------------------------------------


class TestFindById:
    def test_find_existing(self, client: TestClient) -> None:
        created = _create(client, name="Dave", email="dave@example.com").json()
        resp = client.get(f"/customers/{created['id']}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Dave"

    def test_find_non_existing_returns_404(self, client: TestClient) -> None:
        resp = client.get("/customers/9999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Find By Name
# ---------------------------------------------------------------------------


class TestFindByName:
    def test_find_by_exact_name(self, client: TestClient) -> None:
        _create(client, name="Eve", email="eve@example.com")
        resp = client.get("/customers/name/Eve")
        assert resp.status_code == 200
        results = resp.json()
        assert len(results) == 1
        assert results[0]["name"] == "Eve"

    def test_find_by_partial_name(self, client: TestClient) -> None:
        _create(client, name="Frank Sinatra", email="frank@example.com")
        resp = client.get("/customers/name/frank")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_find_by_name_no_match(self, client: TestClient) -> None:
        resp = client.get("/customers/name/NoSuchPerson")
        assert resp.status_code == 200
        assert resp.json() == []


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------


class TestUpdateCustomer:
    def test_update_name(self, client: TestClient) -> None:
        created = _create(client, name="Grace", email="grace@example.com").json()
        resp = client.put(
            f"/customers/{created['id']}", json={"name": "Grace Updated"}
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "Grace Updated"

    def test_update_non_existing_returns_404(self, client: TestClient) -> None:
        resp = client.put("/customers/9999", json={"name": "X"})
        assert resp.status_code == 404

    def test_update_to_duplicate_email_returns_400(self, client: TestClient) -> None:
        _create(client, email="h1@example.com")
        c2 = _create(client, name="H2", email="h2@example.com").json()
        resp = client.put(
            f"/customers/{c2['id']}", json={"email": "h1@example.com"}
        )
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------


class TestDeleteCustomer:
    def test_delete_existing_returns_204(self, client: TestClient) -> None:
        created = _create(client, email="del@example.com").json()
        resp = client.delete(f"/customers/{created['id']}")
        assert resp.status_code == 204

    def test_delete_removes_customer(self, client: TestClient) -> None:
        created = _create(client, email="gone@example.com").json()
        client.delete(f"/customers/{created['id']}")
        resp = client.get(f"/customers/{created['id']}")
        assert resp.status_code == 404

    def test_delete_non_existing_returns_404(self, client: TestClient) -> None:
        resp = client.delete("/customers/9999")
        assert resp.status_code == 404
