
from fastapi import APIRouter, HTTPException

from app.database import supabase

router = APIRouter(tags=["Health"])


@router.get("/")
def root():
    return {
        "message": "Transaction Ledger API is running"
    }


@router.get("/health")
def health():
    try:
        supabase.table("accounts").select("id").limit(1).execute()

        return {
            "status": "ok",
            "database": "connected",
        }

    except Exception as error:
        print("Health-check error:", repr(error))

        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "database": "unavailable",
            },
        )
