"""Customer controller — HTTP layer (Flask Blueprint)."""

from flask import Blueprint, request, jsonify

from app.services.customer_service import CustomerService

customer_bp = Blueprint("customers", __name__, url_prefix="/customers")
_service = CustomerService()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _ok(data, status: int = 200):
    return jsonify(data), status


def _error(message: str, status: int = 400):
    return jsonify({"error": message}), status


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@customer_bp.route("", methods=["POST"])
def create_customer():
    """Create a new customer.

    **Request body** (JSON):

    .. code-block:: json

        {
            "name":    "João Silva",
            "email":   "joao@example.com",
            "phone":   "11999990000",
            "address": "Rua das Flores, 123"
        }

    ``name`` and ``email`` are required; ``phone`` and ``address`` are
    optional.

    **Responses**:

    - ``201 Created`` — customer created successfully.
    - ``400 Bad Request`` — validation error or duplicate e-mail.
    """
    data = request.get_json(silent=True) or {}
    customer, error = _service.create_customer(data)
    if error:
        return _error(error, 400)
    return _ok(customer.to_dict(), 201)


# ---------------------------------------------------------------------------
# Read — collection
# ---------------------------------------------------------------------------

@customer_bp.route("", methods=["GET"])
def find_all():
    """Return all customers.

    **Responses**:

    - ``200 OK`` — list of customer objects.
    """
    customers = _service.get_all_customers()
    return _ok([c.to_dict() for c in customers])


@customer_bp.route("/count", methods=["GET"])
def count():
    """Return the total number of customers.

    **Responses**:

    - ``200 OK`` — ``{"count": <int>}``.
    """
    return _ok({"count": _service.count_customers()})


@customer_bp.route("/name/<string:name>", methods=["GET"])
def find_by_name(name: str):
    """Return customers whose name contains *name* (case-insensitive).

    **Path parameter**: ``name`` — substring to search.

    **Responses**:

    - ``200 OK`` — list of matching customer objects.
    """
    customers = _service.get_customers_by_name(name)
    return _ok([c.to_dict() for c in customers])


# ---------------------------------------------------------------------------
# Read — single item
# ---------------------------------------------------------------------------

@customer_bp.route("/<int:customer_id>", methods=["GET"])
def find_by_id(customer_id: int):
    """Return a single customer by ID.

    **Path parameter**: ``customer_id`` — integer primary key.

    **Responses**:

    - ``200 OK`` — customer object.
    - ``404 Not Found`` — no customer with that ID.
    """
    customer = _service.get_customer_by_id(customer_id)
    if customer is None:
        return _error(f"Customer with id {customer_id} not found.", 404)
    return _ok(customer.to_dict())


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@customer_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id: int):
    """Update an existing customer.

    **Path parameter**: ``customer_id`` — integer primary key.

    **Request body** (JSON): any subset of ``name``, ``email``, ``phone``,
    ``address``.

    **Responses**:

    - ``200 OK`` — updated customer object.
    - ``400 Bad Request`` — duplicate e-mail or validation error.
    - ``404 Not Found`` — no customer with that ID.
    """
    data = request.get_json(silent=True) or {}
    customer, error, status = _service.update_customer(customer_id, data)
    if error:
        return _error(error, status)
    return _ok(customer.to_dict())


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@customer_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id: int):
    """Delete a customer by ID.

    **Path parameter**: ``customer_id`` — integer primary key.

    **Responses**:

    - ``204 No Content`` — customer deleted.
    - ``404 Not Found`` — no customer with that ID.
    """
    error, status = _service.delete_customer(customer_id)
    if error:
        return _error(error, status)
    return "", 204
