# Sales — API de Clientes

API RESTful seguindo o padrão **MVC** que implementa operações CRUD básicas para os clientes de uma loja.

---

## Índice

1. [Requisitos](#requisitos)
2. [Primeiros Passos](#primeiros-passos)
3. [Estrutura de Pastas](#estrutura-de-pastas)
4. [Arquitetura](#arquitetura)
5. [Referência da API](#referência-da-api)
6. [Executando os Testes](#executando-os-testes)

---

## Requisitos

- Python 3.10+
- pip

---

## Primeiros Passos

```bash
# 1. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Inicie o servidor (padrão: http://127.0.0.1:8000)
python run.py
```

O arquivo de banco de dados SQLite (`sales.db`) é criado automaticamente na raiz do projeto na primeira execução.

---

## Estrutura de Pastas

```
sales/
├── app/                        # Pacote da aplicação
│   ├── __init__.py             # Fábrica do app (create_app), exception handler, rota home
│   ├── database.py             # Engine SQLAlchemy, SessionLocal, Base e get_db()
│   ├── templates/              # Templates HTML
│   │   └── home.html           # Página inicial com links para /docs e /redoc
│   ├── models/                 # Camada MODEL — definições ORM
│   │   ├── __init__.py
│   │   └── customer.py         # Modelo SQLAlchemy de Customer
│   ├── schemas/                # Schemas Pydantic — validação de entrada e saída
│   │   ├── __init__.py
│   │   └── customer.py         # CustomerCreate, CustomerUpdate, CustomerResponse, …
│   ├── repositories/           # Camada REPOSITORY — acesso a dados (consultas ORM)
│   │   ├── __init__.py
│   │   └── customer_repository.py
│   ├── services/               # Camada SERVICE — lógica de negócio
│   │   ├── __init__.py
│   │   ├── exceptions.py       # Exceções de domínio (NotFoundError, DuplicateError, …)
│   │   └── customer_service.py
│   └── controllers/            # Camada CONTROLLER — rotas HTTP
│       ├── __init__.py
│       └── customer_controller.py  # FastAPI Router /customers
├── tests/                      # Suíte de testes automatizados (pytest)
│   ├── __init__.py
│   └── test_customer.py
├── config.py                   # Configuração (DATABASE_URL via variável de ambiente)
├── requirements.txt            # Dependências Python
├── run.py                      # Ponto de entrada — cria tabelas e inicia Uvicorn
└── README.md
```

### Responsabilidades dos Componentes

| Camada | Pasta / Arquivo | Responsabilidade |
|---|---|---|
| **Model** | `app/models/` | Define o esquema de dados via SQLAlchemy ORM (mapeamento objeto-relacional). |
| **Schema** | `app/schemas/` | Valida entrada e serializa saída com Pydantic (`CustomerCreate`, `CustomerResponse`, etc.). |
| **Controller** | `app/controllers/` | Recebe requisições HTTP, delega ao Service e retorna respostas HTTP. |
| **Service** | `app/services/` | Contém regras de negócio: validação de dados, tratamento de erros e orquestração. |
| **Repository** | `app/repositories/` | Abstrai todas as consultas ao banco de dados via sessão SQLAlchemy. |
| **Database** | `app/database.py` | Cria o engine, a session factory (`SessionLocal`) e fornece `get_db()` para injeção de dependência. |
| **Config** | `config.py` | Carrega variáveis de configuração (`DATABASE_URL`) a partir do ambiente. |
| **View** | Respostas JSON | O FastAPI retorna JSON automaticamente — não há camada de templates HTML. |

> O padrão Repository é adicionado entre o Service e o Model para manter a camada de Service independente da implementação do ORM.

---

## Arquitetura

### C4 — Diagrama de Contexto (Nível 1)

```mermaid
flowchart TD
    Cliente["<b>Cliente</b><br><i>[Pessoa]</i><br><br>Usuário que consome a API<br>(navegador / Postman / frontend)"]
    SalesAPI["<b>Sales API</b><br><i>[Sistema]</i><br><br>API RESTful para gestão de<br>clientes (operações CRUD)"]
    DB[("<b>Banco de Dados</b><br><i>[SQLite — sales.db]</i><br><br>Armazena registros de clientes")]

    Cliente -->|"HTTP/JSON"| SalesAPI
    SalesAPI -->|"SQL (SQLAlchemy)"| DB
```

### C4 — Diagrama de Container (Nível 2)

```mermaid
flowchart TD
    Cliente["Cliente"]
    Cliente -->|"HTTP/JSON"| AppContent

    subgraph Servidor["Servidor (run.py)"]
        subgraph Uvicorn["Uvicorn — ASGI Server (:8000)"]
            subgraph FastAPIApp["Aplicação FastAPI (create_app)"]
                AppContent["• Exception Handler global<br>• Rota GET / (Home — links para docs)<br>• Customer Router (/customers)<br>• Swagger UI (/docs) · ReDoc (/redoc)"]
            end
        end
        Config["config.py<br>DATABASE_URL"] --> DatabasePy["database.py<br>engine · SessionLocal · get_db()"]
    end

    DatabasePy -->|"SQL"| SQLite[("SQLite (sales.db)")]
```

### C4 — Diagrama de Componentes (Nível 3)

```mermaid
flowchart TD
    Req(["Requisição HTTP"])
    Req --> AppFactory

    subgraph App["Aplicação FastAPI"]
        AppFactory["<b>App Factory</b> — app/__init__.py<br>• Exception Handler<br>• Rota GET /<br>• Registra o Customer Router"]
        AppFactory --> Controller

        Schemas["<b>Schemas (Pydantic)</b><br>CustomerCreate (entrada)<br>CustomerUpdate (entrada)<br>CustomerResponse (saída)<br>CountResponse (saída)<br>ErrorResponse (saída)"]
        Schemas -.-> Controller

        Controller["<b>Controller</b> — APIRouter<br>POST /customers · GET /customers<br>GET /customers/count · GET /customers/:id<br>GET /customers/name/:name<br>PUT /customers/:id · DELETE /customers/:id"]

        Controller -->|"Depends(_get_service)"| Service

        Service["<b>Service</b> — lógica de negócio<br>• strip / validação<br>• trata duplicatas<br>• orquestra CRUD"]
        Service --> Repository

        Repository["<b>Repository</b> — acesso a dados<br>• add / query<br>• commit / refresh<br>• delete"]
        Model["<b>Model (ORM)</b> — Customer<br>id : Integer (PK) · name : String(100)<br>email : String(150) UQ · phone : String(20)<br>address : String(255)"]

        Repository -->|usa| Model
        Repository -->|"Depends(get_db)"| DatabasePy

        DatabasePy["<b>database.py</b><br>engine · SessionLocal · Base · get_db()"]
    end

    DatabasePy -->|"SQL"| SQLite[("SQLite (sales.db)")]
```

### UML — Diagrama de Classes

```mermaid
classDiagram
    direction TB

    class CustomerCreate {
        +name : str
        +email : str
        +phone : str | None
        +address : str | None
    }

    class CustomerUpdate {
        +name : str | None
        +email : str | None
        +phone : str | None
        +address : str | None
    }

    class CustomerResponse {
        <<from_attributes=True>>
        +id : int
        +name : str
        +email : str
        +phone : str | None
        +address : str | None
    }

    class CountResponse {
        +count : int
    }

    class ErrorResponse {
        +error : str
    }

    class CustomerController {
        <<APIRouter>>
        POST /customers
        GET /customers
        GET /customers/count
        GET /customers/:id
        GET /customers/name/:name
        PUT /customers/:id
        DELETE /customers/:id
    }

    class CustomerService {
        +create_customer(data)
        +update_customer(id, data)
        +delete_customer(id)
        +get_all_customers()
        +get_customer_by_id(id)
        +get_customers_by_name(name)
        +count_customers()
    }

    class CustomerRepository {
        +create(name, email, ...) Customer
        +find_all() list
        +find_by_id(id) Customer
        +find_by_name(n) list
        +count() int
        +update(c, ...) Customer
        +delete(c) None
    }

    class Customer {
        <<Model>>
        +id : Integer PK
        +name : String~100~
        +email : String~150~ UNIQUE
        +phone : String~20~
        +address : String~255~
    }

    CustomerCreate ..> CustomerController : valida
    CustomerUpdate ..> CustomerController : valida
    CustomerResponse ..> CustomerController : serializa
    CountResponse ..> CustomerController : serializa
    ErrorResponse ..> CustomerController : serializa
    CustomerController --> CustomerService : usa
    CustomerService --> CustomerRepository : usa
    CustomerRepository --> Customer : usa
```

### Fluxo de uma Requisição

```mermaid
flowchart TD
    Req(["Requisição HTTP<br>(ex: POST /customers)"])
    Req --> Uvicorn["<b>Uvicorn</b><br>servidor ASGI recebe a conexão<br>e encaminha ao FastAPI"]
    Uvicorn --> Factory["<b>App Factory</b><br>exception handler registrado<br>para capturar erros"]
    Factory --> SchemaIn["<b>Schema</b><br>Pydantic valida o corpo da<br>requisição (CustomerCreate)"]
    SchemaIn --> Ctrl["<b>Controller</b><br>extrai dados validados,<br>obtém Service via Depends"]
    Ctrl --> Svc["<b>Service</b><br>aplica regras de negócio<br>(strip, campos obrigatórios, duplicatas)"]
    Svc --> Repo["<b>Repository</b><br>executa operação ORM<br>(add + commit + refresh)"]
    Repo --> ModelDB["<b>Model / DB</b><br>SQLAlchemy persiste no SQLite<br>via engine (database.py)"]
    ModelDB -.->|"caminho inverso"| SchemaOut["<b>Schema</b><br>CustomerResponse serializa<br>o modelo ORM para JSON"]
    SchemaOut --> Resp(["Resposta HTTP<br>(JSON — status 201)"])
```

---

## Referência da API

URL Base: `http://127.0.0.1:8000`

### Objeto Customer

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

| Método | Caminho | Descrição |
|--------|---------|-----------|
| `POST` | `/customers` | Criar um novo cliente |
| `GET` | `/customers` | Retornar todos os clientes |
| `GET` | `/customers/count` | Retornar o número total de clientes |
| `GET` | `/customers/{id}` | Retornar cliente por ID |
| `GET` | `/customers/name/{name}` | Retornar clientes que correspondem ao nome |
| `PUT` | `/customers/{id}` | Atualizar um cliente existente |
| `DELETE` | `/customers/{id}` | Excluir um cliente |

#### POST `/customers`

**Corpo** (JSON):

```json
{
  "name":    "João Silva",        // obrigatório
  "email":   "joao@example.com", // obrigatório, único
  "phone":   "11999990000",      // opcional
  "address": "Rua das Flores, 1" // opcional
}
```

Respostas: `201 Created` | `400 Bad Request`

#### GET `/customers`

Respostas: `200 OK` — array de objetos de cliente.

#### GET `/customers/count`

Respostas: `200 OK` — `{"count": 42}`

#### GET `/customers/{id}`

Respostas: `200 OK` | `404 Not Found`

#### GET `/customers/name/{name}`

Busca por substring sem distinção entre maiúsculas e minúsculas.

Respostas: `200 OK` — array de objetos de cliente correspondentes.

#### PUT `/customers/{id}`

**Corpo** (JSON): qualquer subconjunto de `name`, `email`, `phone`, `address`.

Respostas: `200 OK` | `400 Bad Request` | `404 Not Found`

#### DELETE `/customers/{id}`

Respostas: `204 No Content` | `404 Not Found`

---

## Executando os Testes

```bash
pip install pytest
python -m pytest tests/ -v
```