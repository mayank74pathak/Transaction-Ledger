
from fastapi import FastAPI

from app.routers import (
    accounts,
    health,
    transactions,
    transfers,
)

# Initialize the FastAPI application
app = FastAPI(
    title="Transaction Ledger API",
    description=(
        "REST API for account management, "
        "credit/debit transactions, and money transfers."
    ),
    version="1.0.0",
)

# Register API routers
app.include_router(health.router)
app.include_router(accounts.router)
app.include_router(transactions.router)
app.include_router(transfers.router)
