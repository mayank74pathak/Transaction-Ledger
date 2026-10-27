
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from app.database import supabase
from app.schemas import TransactionCreate
from app.services.ledger_service import process_transaction

router = APIRouter(tags=["Transactions"])


@router.post("/transactions", status_code=201)
def create_transaction(transaction: TransactionCreate):
    reference_id = transaction.reference_id.strip()

    if not reference_id:
        raise HTTPException(
            status_code=422,
            detail="Reference ID cannot be empty",
        )

    result = process_transaction(
        account_id=transaction.account_id,
        transaction_type=transaction.type,
        amount=transaction.amount,
        description=transaction.description,
        reference_id=reference_id,
    )

    return {
        "message": "Transaction processed successfully",
        "transaction": result,
    }


@router.get("/accounts/{account_id}/transactions")
def get_transaction_history(
    account_id: UUID,
    type: Literal["credit", "debit"] | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    try:
        account_result = (
            supabase.table("accounts")
            .select("id")
            .eq("id", str(account_id))
            .execute()
        )

        if not account_result.data:
            raise HTTPException(
                status_code=404,
                detail="Account not found",
            )

        offset = (page - 1) * limit

        query = (
            supabase.table("transactions")
            .select("*", count="exact")
            .eq("account_id", str(account_id))
        )

        if type is not None:
            query = query.eq("type", type)

        result = (
            query
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        total = result.count or 0
        total_pages = (total + limit - 1) // limit

        return {
            "account_id": str(account_id),
            "transactions": result.data,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": limit,
                "total_pages": total_pages,
            },
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Transaction history error:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve transaction history",
        )
