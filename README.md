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

# 3. Inicie o servidor (padrão: http://127.0.0.1:5000)
python run.py
```

O arquivo de banco de dados SQLite (`sales.db`) é criado automaticamente na raiz do projeto na primeira execução.

---

## Estrutura de Pastas

```
sales/
├── app/                        # Pacote da aplicação
│   ├── __init__.py             # Fábrica do app (create_app) + instância do db
│   ├── models/                 # Camada MODEL — estruturas de dados
│   │   ├── __init__.py
│   │   └── customer.py         # Modelo SQLAlchemy de Customer
│   ├── repositories/           # Camada de acesso a dados (consultas ORM)
│   │   ├── __init__.py
│   │   └── customer_repository.py
│   ├── services/               # Camada SERVICE — lógica de negócio
│   │   ├── __init__.py
│   │   └── customer_service.py
│   └── controllers/            # Camada CONTROLLER — rotas HTTP
│       ├── __init__.py
│       └── customer_controller.py  # FastAPI Blueprint /customers
├── tests/                      # Suíte de testes automatizados (pytest)
│   ├── __init__.py
│   └── test_customer.py
├── config.py                   # Classes de configuração (padrão + testes)
├── requirements.txt            # Dependências Python
├── run.py                      # Ponto de entrada
└── README.md
```

### Responsabilidades dos Componentes (MVC)

| Camada | Pasta | Responsabilidade |
|---|---|---|
| **Model** | `app/models/` | Define o esquema de dados (SQLAlchemy ORM). Fornece `to_dict()` para serialização. |
| **View** | Respostas JSON | O FastAPI retorna JSON — não há camada de templates HTML. |
| **Controller** | `app/controllers/` | Recebe requisições HTTP, delega ao Service e retorna respostas HTTP. |
| **Service** | `app/services/` | Contém regras de negócio: validação de entrada, tratamento de erros, orquestração. |
| **Repository** | `app/repositories/` | Abstrai todas as consultas ao banco de dados. Única camada que importa `db`. |

> O padrão Repository é adicionado entre o Service e o Model para manter a camada de Service independente da implementação do ORM.

---

## Arquitetura

### C4 — Diagrama de Contexto

```
┌─────────────────────────────────────────────────────────┐
│                        Cliente                          │
│              (navegador / Postman / frontend)           │
└───────────────────────────┬─────────────────────────────┘
                            │  HTTP/JSON
                            ▼
┌──────────────────────────────────────────────────────── ┐
│                    Sales API (FastAPI)                  │
│                                                         │
│  ┌──────────────┐     ┌──────────────┐    ┌──────────┐  │
│  │  Controller  │───▶│   Service    │───▶│  Repo.   │  │
│  │  (rotas)     │     │ (neg./lóg.)  │    │  (ORM)   │  │
│  └──────────────┘     └──────────────┘    └────┬─────┘  │
│                                                │        │
└─────────────────────────────────────────────── ┼────────┘
                                                 │ SQL
                                                 ▼
                                    ┌───────────────────┐
                                    │  Banco de Dados   │
                                    │     SQLite        │
                                    └───────────────────┘
```

### UML — Diagrama de Classes

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
           ▲ usa
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
           ▲ usa
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
           ▲ usa
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

### Fluxo de uma Requisição

```
Requisição HTTP
     │
     ▼
[Controller] ──── valida o HTTP, extrai o payload
     │
     ▼
[Service]    ──── valida as regras de negócio
     │
     ▼
[Repository] ──── executa a consulta ORM
     │
     ▼
[Model / DB] ──── persiste ou busca dados
     │
     ▼ (caminho inverso)
Resposta HTTP (JSON)
```

---

## Referência da API

URL Base: `http://127.0.0.1:5000`

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