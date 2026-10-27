
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


# Request model for creating an account
class AccountCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )


# Request model for credit and debit transactions
class TransactionCreate(BaseModel):
    account_id: UUID

    type: Literal["credit", "debit"]

    amount: Decimal = Field(
        gt=0,
        max_digits=14,
        decimal_places=2,
    )

    description: str = Field(
        default="",
        max_length=500,
    )

    reference_id: str = Field(
        min_length=1,
        max_length=100,
    )


# Request model for transferring money
class TransferCreate(BaseModel):
    from_account_id: UUID

    to_account_id: UUID

    amount: Decimal = Field(
        gt=0,
        max_digits=14,
        decimal_places=2,
    )

    description: str = Field(
        default="Money transfer",
        max_length=500,
    )

    reference_id: str = Field(
        min_length=1,
        max_length=100,
    )
