# Transaction Ledger API

A RESTful backend API built with **FastAPI** and **Supabase PostgreSQL** for managing accounts and financial ledger transactions. The project uses a modular structure that separates API routes, request validation, database configuration, and transaction service logic.

## Features

- Create accounts with an initial balance of `0`.
- Record credit and debit transactions.
- Reject debits when the account has insufficient funds.
- Prevent duplicate transaction references within the same account.
- Retrieve account balances.
- Retrieve transaction history with optional type filtering and pagination.
- Return transactions in newest-first order.
- Transfer money between two accounts.
- Check API and database health.
- Interactive API documentation through Swagger UI.

## Tech Stack

- Python
- FastAPI
- Pydantic
- Supabase Python client
- Supabase PostgreSQL
- PostgreSQL PL/pgSQL RPC functions
- Uvicorn

## Project Structure

```text
transaction-ledger/
├── README.md
└── fastapi-backend/
    ├── app/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── database.py
    │   ├── schemas.py
    │   ├── routers/
    │   │   ├── __init__.py
    │   │   ├── health.py
    │   │   ├── accounts.py
    │   │   ├── transactions.py
    │   │   └── transfers.py
    │   └── services/
    │       ├── __init__.py
    │       └── ledger_service.py
    ├── .env
    ├── .gitignore
    └── requirements.txt
```

### Responsibilities

| File | Responsibility |
|---|---|
| `app/main.py` | Creates the FastAPI app and registers routers |
| `app/database.py` | Loads environment variables and creates the Supabase client |
| `app/schemas.py` | Defines Pydantic request models and validation |
| `app/routers/health.py` | Root and database health-check endpoints |
| `app/routers/accounts.py` | Account creation and balance lookup |
| `app/routers/transactions.py` | Credit/debit requests and transaction history |
| `app/routers/transfers.py` | Money transfer endpoint |
| `app/services/ledger_service.py` | Calls PostgreSQL RPC functions and maps errors |

## Prerequisites

- Python 3.10 or newer recommended
- A Supabase project
- Git (optional, for version control)

## Setup and Installation

### 1. Go to the backend directory

```bash
cd fastapi-backend
```

If your terminal is already inside `fastapi-backend`, skip this step.

### 2. Create and activate a virtual environment

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` has not yet been created, install the packages directly:

```bash
pip install fastapi "uvicorn[standard]" python-dotenv supabase pydantic
```

### 4. Configure environment variables

Create a `.env` file in `fastapi-backend/`:

```dotenv
SUPABASE_URL=https://YOUR_PROJECT.supabase.co
SUPABASE_SERVICE_ROLE_KEY=YOUR_SERVER_SIDE_KEY
```

Replace the placeholders with your own Supabase project URL and server-side key. The URL should be the project URL, not a URL ending in `/rest/v1`.

The variable names must match the ones used in `app/database.py`.

> **Security:** Keep `.env` private. Never commit credentials to GitHub or expose the service-role/secret key in frontend code.

### 5. Configure the database

The backend expects Supabase PostgreSQL tables for `accounts` and `transactions`, plus these RPC functions:

- `process_transaction` — validates and records a credit/debit transaction and updates the account balance.
- `transfer_money` — records the transfer's debit and credit entries and updates both account balances atomically.

Create these tables and functions in the Supabase SQL Editor before testing the corresponding endpoints. The RPC function parameter names must match the names passed in `app/services/ledger_service.py`.

## Run the Application

Run this command from the **`fastapi-backend/` directory**:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The import path is `app.main:app` because the FastAPI application variable is named `app` in `app/main.py`.

Open these URLs after the server starts:

- API root: <http://127.0.0.1:8000/>
- Database health check: <http://127.0.0.1:8000/health>
- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI schema: <http://127.0.0.1:8000/openapi.json>

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Check whether the API is running |
| `GET` | `/health` | Check database connectivity |
| `POST` | `/accounts` | Create an account |
| `GET` | `/accounts/{account_id}/balance` | Retrieve account details and balance |
| `POST` | `/transactions` | Create a credit or debit transaction |
| `GET` | `/accounts/{account_id}/transactions` | Retrieve transaction history |
| `POST` | `/transfers` | Transfer money between accounts |

## Example Requests

Use real account UUIDs returned by the API. The UUIDs below are placeholders.

### Create an account

`POST /accounts`

```json
{
  "name": "Alice"
}
```

New accounts should start with a balance of `0`; the client does not provide the initial balance.

### Credit an account

`POST /transactions`

```json
{
  "account_id": "11111111-1111-4111-8111-111111111111",
  "type": "credit",
  "amount": 1000.00,
  "description": "Initial deposit",
  "reference_id": "TXN-001"
}
```

### Debit an account

`POST /transactions`

```json
{
  "account_id": "11111111-1111-4111-8111-111111111111",
  "type": "debit",
  "amount": 100.00,
  "description": "Payment",
  "reference_id": "TXN-002"
}
```

A debit should be rejected when the account does not have sufficient funds.

### Get an account balance

`GET /accounts/{account_id}/balance`

```text
GET /accounts/11111111-1111-4111-8111-111111111111/balance
```

### Get transaction history

`GET /accounts/{account_id}/transactions?page=1&limit=10`

Optional query parameters:

- `type=credit` or `type=debit`
- `page` — page number, minimum `1`
- `limit` — page size between `1` and `100`

Example:

```text
GET /accounts/11111111-1111-4111-8111-111111111111/transactions?type=credit&page=1&limit=10
```

The response includes transaction records and pagination metadata: total records, current page, page size, and total pages.

### Transfer money

`POST /transfers`

```json
{
  "from_account_id": "11111111-1111-4111-8111-111111111111",
  "to_account_id": "33333333-3333-4333-8333-333333333333",
  "amount": 200.00,
  "description": "Transfer between accounts",
  "reference_id": "TRANSFER-001"
}
```

Both accounts must exist and must be different. The database function must ensure the debit and credit happen atomically, so a partial transfer cannot be committed.

## Error Handling

The API maps common failures to HTTP status codes:

| Status | Meaning |
|---|---|
| `400` | Insufficient balance |
| `404` | Account or transfer participant not found |
| `409` | Duplicate transaction/transfer reference |
| `422` | Invalid request data or invalid operation details |
| `500` | Unexpected server or database error |
| `503` | Database health check failed |

## Suggested Testing Checklist

- [ ] Health check reports a database connection.
- [ ] Create an account and verify the initial balance is `0`.
- [ ] Credit an account and verify the balance.
- [ ] Debit an account and verify the balance.
- [ ] Attempt a debit that exceeds the available balance.
- [ ] Reuse a reference ID on the same account and verify it is rejected.
- [ ] Reuse a reference ID on a different account and verify it is allowed.
- [ ] Test transaction history filtering, pagination, and newest-first sorting.
- [ ] Transfer money between two accounts and verify both balances and histories.
- [ ] Attempt transfers with missing accounts, identical accounts, insufficient funds, and duplicate references.

## Security and Design Notes

- Keep the Supabase server-side key in the backend environment only.
- Ensure `.env` is listed in `.gitignore`.
- Use database constraints for data integrity, including unique references per account and foreign keys.
- Keep balance updates and ledger inserts inside PostgreSQL functions to preserve atomicity.
- The current implementation does not include end-user authentication or authorization. Add appropriate controls before public deployment.
- Test all endpoints locally before deployment.

## Assignment Submission

Suggested deliverables:

1. Source code
2. `README.md`
3. API documentation
4. `ASSUMPTIONS.md`

Do not include `.env`, virtual environment files, or credentials in the submission.
