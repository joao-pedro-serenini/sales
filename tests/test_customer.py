"""Tests for the Customer API endpoints."""

import pytest

from app import create_app, db
from config import TestingConfig


@pytest.fixture
def app():
    """Create a test Flask application with an in-memory SQLite database."""
    application = create_app(TestingConfig)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Return a test client for the application."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _create(client, **kwargs):
    payload = {"name": "Test User", "email": "test@example.com"}
    payload.update(kwargs)
    return client.post("/customers", json=payload)


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

class TestCreateCustomer:
    def test_create_returns_201(self, client):
        resp = _create(client)
        assert resp.status_code == 201

    def test_create_returns_customer_data(self, client):
        resp = _create(client, name="Alice", email="alice@example.com")
        data = resp.get_json()
        assert data["name"] == "Alice"
        assert data["email"] == "alice@example.com"
        assert data["id"] is not None

    def test_create_missing_name_returns_400(self, client):
        resp = client.post("/customers", json={"email": "a@b.com"})
        assert resp.status_code == 400

    def test_create_missing_email_returns_400(self, client):
        resp = client.post("/customers", json={"name": "Bob"})
        assert resp.status_code == 400

    def test_create_duplicate_email_returns_400(self, client):
        _create(client, email="dup@example.com")
        resp = _create(client, email="dup@example.com")
        assert resp.status_code == 400

    def test_create_with_optional_fields(self, client):
        resp = client.post(
            "/customers",
            json={
                "name": "Carol",
                "email": "carol@example.com",
                "phone": "11999990000",
                "address": "Rua das Flores, 1",
            },
        )
        data = resp.get_json()
        assert data["phone"] == "11999990000"
        assert data["address"] == "Rua das Flores, 1"


# ---------------------------------------------------------------------------
# Find All
# ---------------------------------------------------------------------------

class TestFindAll:
    def test_empty_returns_empty_list(self, client):
        resp = client.get("/customers")
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_all_customers(self, client):
        _create(client, name="A", email="a@a.com")
        _create(client, name="B", email="b@b.com")
        resp = client.get("/customers")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 2


# ---------------------------------------------------------------------------
# Count
# ---------------------------------------------------------------------------

class TestCount:
    def test_count_zero(self, client):
        resp = client.get("/customers/count")
        assert resp.status_code == 200
        assert resp.get_json() == {"count": 0}

    def test_count_after_creates(self, client):
        _create(client, email="x1@x.com")
        _create(client, email="x2@x.com")
        resp = client.get("/customers/count")
        assert resp.get_json() == {"count": 2}


# ---------------------------------------------------------------------------
# Find By ID
# ---------------------------------------------------------------------------

class TestFindById:
    def test_find_existing(self, client):
        created = _create(client, name="Dave", email="dave@example.com").get_json()
        resp = client.get(f"/customers/{created['id']}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Dave"

    def test_find_non_existing_returns_404(self, client):
        resp = client.get("/customers/9999")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Find By Name
# ---------------------------------------------------------------------------

class TestFindByName:
    def test_find_by_exact_name(self, client):
        _create(client, name="Eve", email="eve@example.com")
        resp = client.get("/customers/name/Eve")
        assert resp.status_code == 200
        results = resp.get_json()
        assert len(results) == 1
        assert results[0]["name"] == "Eve"

    def test_find_by_partial_name(self, client):
        _create(client, name="Frank Sinatra", email="frank@example.com")
        resp = client.get("/customers/name/frank")
        assert resp.status_code == 200
        assert len(resp.get_json()) == 1

    def test_find_by_name_no_match(self, client):
        resp = client.get("/customers/name/NoSuchPerson")
        assert resp.status_code == 200
        assert resp.get_json() == []


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class TestUpdateCustomer:
    def test_update_name(self, client):
        created = _create(client, name="Grace", email="grace@example.com").get_json()
        resp = client.put(f"/customers/{created['id']}", json={"name": "Grace Updated"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Grace Updated"

    def test_update_non_existing_returns_404(self, client):
        resp = client.put("/customers/9999", json={"name": "X"})
        assert resp.status_code == 404

    def test_update_to_duplicate_email_returns_400(self, client):
        _create(client, email="h1@example.com")
        c2 = _create(client, name="H2", email="h2@example.com").get_json()
        resp = client.put(f"/customers/{c2['id']}", json={"email": "h1@example.com"})
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class TestDeleteCustomer:
    def test_delete_existing_returns_204(self, client):
        created = _create(client, email="del@example.com").get_json()
        resp = client.delete(f"/customers/{created['id']}")
        assert resp.status_code == 204

    def test_delete_removes_customer(self, client):
        created = _create(client, email="gone@example.com").get_json()
        client.delete(f"/customers/{created['id']}")
        resp = client.get(f"/customers/{created['id']}")
        assert resp.status_code == 404

    def test_delete_non_existing_returns_404(self, client):
        resp = client.delete("/customers/9999")
        assert resp.status_code == 404
