# Transaction Ledger — Streamlit Frontend

A basic Streamlit UI for the Transaction Ledger FastAPI backend.

## Features
- Backend health check
- Create account (account starts with balance 0 on the backend)
- Select account using its UUID and view balance
- Submit credit/debit transactions
- Transfer funds between two accounts
- View filtered, paginated transaction history

## Requirements
- Python 3.10+
- A running FastAPI backend with the endpoints below
- Streamlit and Requests

## Run locally

From this directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

The UI uses `http://127.0.0.1:8000` by default. You can change the FastAPI base URL in the sidebar or set `API_BASE_URL` in your environment.

Run the backend separately from `fastapi-backend/`:

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Expected backend endpoints

- `GET /health`
- `POST /accounts`
- `GET /accounts/{account_id}/balance`
- `POST /transactions`
- `GET /accounts/{account_id}/transactions?page=1&limit=10&type=credit`
- `POST /transfers`

The history UI supports API responses shaped as a list or as an object containing `items` or `transactions`.

## Important
- Keep Supabase keys in the FastAPI backend only.
- This is a basic development/demo frontend, not an authenticated production banking UI.
