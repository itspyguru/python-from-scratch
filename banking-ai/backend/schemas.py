from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2)
    email: str
    password: str = Field(min_length=6)


class UserOut(BaseModel):
    id: int
    name: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AccountOut(BaseModel):
    account_number: str
    account_type: str
    balance: Decimal
    currency: str


class BeneficiaryCreate(BaseModel):
    name: str
    account_number: str = Field(min_length=12, max_length=12)


class BeneficiaryOut(BaseModel):
    id: int
    name: str
    account_number: str


class MoneyIn(BaseModel):
    account_number: str
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class TransferIn(BaseModel):
    from_account: str
    to_account: str
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    note: str | None = None


class TransactionOut(BaseModel):
    id: int
    from_account: str | None
    to_account: str | None
    amount: Decimal
    type: str
    status: str
    note: str | None
    created_at: datetime
