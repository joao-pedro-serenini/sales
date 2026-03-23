# Sales — Customer API

RESTful API following the **MVC** pattern that implements basic CRUD operations for the customers of a store.

---

## Table of Contents

1. [Requirements](#requirements)
2. [Getting Started](#getting-started)
3. [Folder Structure](#folder-structure)
4. [Architecture](#architecture)
5. [API Reference](#api-reference)
6. [Running Tests](#running-tests)

---

## Requirements

- Python 3.10+
- pip

---

## Getting Started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server (defaults to http://127.0.0.1:5000)
python run.py
```

The SQLite database file (`sales.db`) is created automatically in the project root on first run.

---

## Folder Structure

```
sales/
├── app/                        # Application package
│   ├── __init__.py             # App factory (create_app) + db instance
│   ├── models/                 # MODEL layer — data structures
│   │   ├── __init__.py
│   │   └── customer.py         # Customer SQLAlchemy model
│   ├── repositories/           # Data-access layer (ORM queries)
│   │   ├── __init__.py
│   │   └── customer_repository.py
│   ├── services/               # SERVICE layer — business logic
│   │   ├── __init__.py
│   │   └── customer_service.py
│   └── controllers/            # CONTROLLER layer — HTTP routes
│       ├── __init__.py
│       └── customer_controller.py  # Flask Blueprint /customers
├── tests/                      # Automated test suite (pytest)
│   ├── __init__.py
│   └── test_customer.py
├── config.py                   # Configuration classes (default + testing)
├── requirements.txt            # Python dependencies
├── run.py                      # Entry point
└── README.md
```

### Component Roles (MVC)

| Layer | Folder | Responsibility |
|---|---|---|
| **Model** | `app/models/` | Defines the data schema (SQLAlchemy ORM). Provides `to_dict()` for serialisation. |
| **View** | JSON responses | Flask returns JSON — there is no HTML template layer. |
| **Controller** | `app/controllers/` | Receives HTTP requests, delegates to the Service, and returns HTTP responses. |
| **Service** | `app/services/` | Contains business rules: input validation, error handling, orchestration. |
| **Repository** | `app/repositories/` | Abstracts all database queries. The only layer that imports `db`. |

> The Repository pattern is added between the Service and Model to keep the Service layer independent of the ORM implementation.

---

## Architecture

### C4 — Context Diagram

```
┌─────────────────────────────────────────────────────────┐
│                        Client                           │
│              (browser / Postman / frontend)             │
└───────────────────────────┬─────────────────────────────┘
                            │  HTTP/JSON
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Sales API (Flask)                    │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │  Controller  │───▶│   Service    │───▶│  Repo.   │  │
│  │  (routes)    │    │ (biz logic)  │    │  (ORM)   │  │
│  └──────────────┘    └──────────────┘    └────┬─────┘  │
│                                               │        │
└───────────────────────────────────────────────┼────────┘
                                                │ SQL
                                                ▼
                                    ┌───────────────────┐
                                    │   SQLite Database  │
                                    └───────────────────┘
```

### UML — Class Diagram

```
┌─────────────────────────────────┐
│          Customer               │
├─────────────────────────────────┤
│ + id       : Integer (PK)       │
│ + name     : String(100)        │
│ + email    : String(150) UNIQUE │
│ + phone    : String(20)         │
│ + address  : String(255)        │
├─────────────────────────────────┤
│ + to_dict() : dict              │
└─────────────────────────────────┘
           ▲ uses
           │
┌──────────────────────────────────┐
│       CustomerRepository         │
├──────────────────────────────────┤
│ + create(name,email,...):Customer│
│ + find_all()       :list         │
│ + find_by_id(id)   :Customer     │
│ + find_by_name(n)  :list         │
│ + count()          :int          │
│ + update(c,...)    :Customer     │
│ + delete(c)        :None         │
└──────────────────────────────────┘
           ▲ uses
           │
┌──────────────────────────────────┐
│        CustomerService           │
├──────────────────────────────────┤
│ + create_customer(data)          │
│ + update_customer(id, data)      │
│ + delete_customer(id)            │
│ + get_all_customers()            │
│ + get_customer_by_id(id)         │
│ + get_customers_by_name(name)    │
│ + count_customers()              │
└──────────────────────────────────┘
           ▲ uses
           │
┌──────────────────────────────────┐
│    CustomerController (Blueprint)│
├──────────────────────────────────┤
│ POST   /customers                │
│ GET    /customers                │
│ GET    /customers/count          │
│ GET    /customers/<id>           │
│ GET    /customers/name/<name>    │
│ PUT    /customers/<id>           │
│ DELETE /customers/<id>           │
└──────────────────────────────────┘
```

### Request Flow

```
HTTP Request
     │
     ▼
[Controller] ──── validates HTTP, extracts payload
     │
     ▼
[Service]    ──── validates business rules
     │
     ▼
[Repository] ──── executes ORM query
     │
     ▼
[Model / DB] ──── persists or fetches data
     │
     ▼ (reversed path)
HTTP Response (JSON)
```

---

## API Reference

Base URL: `http://127.0.0.1:5000`

### Customer Object

```json
{
  "id":      1,
  "name":    "João Silva",
  "email":   "joao@example.com",
  "phone":   "11999990000",
  "address": "Rua das Flores, 123"
}
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/customers` | Create a new customer |
| `GET` | `/customers` | Return all customers |
| `GET` | `/customers/count` | Return total number of customers |
| `GET` | `/customers/{id}` | Return customer by ID |
| `GET` | `/customers/name/{name}` | Return customers matching name |
| `PUT` | `/customers/{id}` | Update an existing customer |
| `DELETE` | `/customers/{id}` | Delete a customer |

#### POST `/customers`

**Body** (JSON):

```json
{
  "name":    "João Silva",        // required
  "email":   "joao@example.com", // required, unique
  "phone":   "11999990000",      // optional
  "address": "Rua das Flores, 1" // optional
}
```

Responses: `201 Created` | `400 Bad Request`

#### GET `/customers`

Responses: `200 OK` — array of customer objects.

#### GET `/customers/count`

Responses: `200 OK` — `{"count": 42}`

#### GET `/customers/{id}`

Responses: `200 OK` | `404 Not Found`

#### GET `/customers/name/{name}`

Case-insensitive substring search.

Responses: `200 OK` — array of matching customer objects.

#### PUT `/customers/{id}`

**Body** (JSON): any subset of `name`, `email`, `phone`, `address`.

Responses: `200 OK` | `400 Bad Request` | `404 Not Found`

#### DELETE `/customers/{id}`

Responses: `204 No Content` | `404 Not Found`

---

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```