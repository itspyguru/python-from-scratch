from datetime import datetime

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    accounts: Mapped[list["Account"]] = relationship(back_populates="user")


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    account_number: Mapped[str] = mapped_column(String(12), unique=True)
    account_type: Mapped[str] = mapped_column(default="savings")
    balance: Mapped[int] = mapped_column(default=0)  # in paise
    currency: Mapped[str] = mapped_column(default="INR")

    user: Mapped[User] = relationship(back_populates="accounts")


class Beneficiary(Base):
    __tablename__ = "beneficiaries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str]
    account_number: Mapped[str] = mapped_column(String(12))


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    from_account: Mapped[str | None]
    to_account: Mapped[str | None]
    amount: Mapped[int]  # in paise
    type: Mapped[str]  # deposit / withdraw / transfer
    status: Mapped[str] = mapped_column(default="completed")
    note: Mapped[str | None]
    idempotency_key: Mapped[str | None] = mapped_column(unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    entries: Mapped[list["LedgerEntry"]] = relationship(back_populates="transaction")


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"))
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    entry_type: Mapped[str]  # debit / credit
    amount: Mapped[int]  # in paise

    transaction: Mapped[Transaction] = relationship(back_populates="entries")
