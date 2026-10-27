
from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.database import supabase
from app.schemas import AccountCreate

router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)


@router.post("", status_code=201)
def create_account(account: AccountCreate):
    name = account.name.strip()

    if not name:
        raise HTTPException(
            status_code=422,
            detail="Account name cannot be empty",
        )

    try:
        result = (
            supabase.table("accounts")
            .insert({"name": name})
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=500,
                detail="Account creation returned no data",
            )

        return {
            "message": "Account created successfully",
            "account": result.data[0],
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Account creation error:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="Failed to create account",
        )


@router.get("/{account_id}/balance")
def get_account_balance(account_id: UUID):
    try:
        result = (
            supabase.table("accounts")
            .select("id, name, balance, created_at")
            .eq("id", str(account_id))
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=404,
                detail="Account not found",
            )

        account = result.data[0]

        return {
            "account_id": account["id"],
            "name": account["name"],
            "balance": account["balance"],
            "created_at": account["created_at"],
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Balance retrieval error:", repr(error))

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve account balance",
        )
