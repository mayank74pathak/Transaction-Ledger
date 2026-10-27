
from fastapi import APIRouter, HTTPException

from app.schemas import TransferCreate
from app.services.ledger_service import process_transfer

router = APIRouter(
    prefix="/transfers",
    tags=["Transfers"],
)


@router.post("", status_code=201)
def transfer_money(transfer: TransferCreate):
    reference_id = transfer.reference_id.strip()

    if not reference_id:
        raise HTTPException(
            status_code=422,
            detail="Reference ID cannot be empty",
        )

    return process_transfer(
        from_account_id=transfer.from_account_id,
        to_account_id=transfer.to_account_id,
        amount=transfer.amount,
        description=transfer.description,
        reference_id=reference_id,
    )
