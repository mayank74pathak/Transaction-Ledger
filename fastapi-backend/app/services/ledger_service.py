
from decimal import Decimal
from uuid import UUID

from fastapi import HTTPException

from app.database import supabase


# --------------------------------------------------
# 1. Process credit/debit transactions
# --------------------------------------------------

def process_transaction(
    account_id: UUID,
    transaction_type: str,
    amount: Decimal,
    description: str,
    reference_id: str,
):
    try:
        result = supabase.rpc(
            "process_transaction",
            {
                "p_account_id": str(account_id),
                "p_type": transaction_type,
                "p_amount": str(amount),
                "p_description": description,
                "p_reference_id": reference_id,
            },
        ).execute()

        return result.data

    except Exception as error:
        message = str(error)
        print("Transaction error:", repr(error))

        if "Account not found" in message:
            raise HTTPException(
                status_code=404,
                detail="Account not found",
            )

        if "Insufficient balance" in message:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance",
            )

        if "Duplicate reference ID" in message:
            raise HTTPException(
                status_code=409,
                detail="Duplicate reference ID",
            )

        if (
            "Invalid transaction" in message
            or "Reference ID is required" in message
        ):
            raise HTTPException(
                status_code=422,
                detail="Invalid transaction details",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to process transaction",
        )


# --------------------------------------------------
# 2. Transfer money between accounts
# --------------------------------------------------

def process_transfer(
    from_account_id: UUID,
    to_account_id: UUID,
    amount: Decimal,
    description: str,
    reference_id: str,
):
    # Prevent transferring money to the same account.
    if from_account_id == to_account_id:
        raise HTTPException(
            status_code=422,
            detail="Source and destination accounts must differ",
        )

    try:
        result = supabase.rpc(
            "transfer_money",
            {
                "p_from_account_id": str(from_account_id),
                "p_to_account_id": str(to_account_id),
                "p_amount": str(amount),
                "p_description": description,
                "p_reference_id": reference_id,
            },
        ).execute()

        return result.data

    except Exception as error:
        message = str(error)
        print("Transfer error:", repr(error))

        if "Source account not found" in message:
            raise HTTPException(
                status_code=404,
                detail="Source account not found",
            )

        if "Destination account not found" in message:
            raise HTTPException(
                status_code=404,
                detail="Destination account not found",
            )

        if "Insufficient balance" in message:
            raise HTTPException(
                status_code=400,
                detail="Insufficient balance",
            )

        if "Duplicate transfer reference ID" in message:
            raise HTTPException(
                status_code=409,
                detail="Duplicate transfer reference ID",
            )

        if (
            "Source and destination must differ" in message
            or "Invalid transfer amount" in message
            or "Transfer reference ID is required" in message
        ):
            raise HTTPException(
                status_code=422,
                detail="Invalid transfer details",
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to process transfer",
        )
