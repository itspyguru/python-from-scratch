import random
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Account, LedgerEntry, Transaction, User


def to_paise(amount: Decimal) -> int:
    return int(amount * 100)


def to_rupees(paise: int) -> Decimal:
    return Decimal(paise) / 100


def new_account_number(db: Session) -> str:
    while True:
        number = "".join(random.choices("0123456789", k=12))
        if db.scalar(select(Account).where(Account.account_number == number)) is None:
            return number


def get_own_account(db: Session, user: User, account_number: str) -> Account:
    account = db.scalar(select(Account).where(Account.account_number == account_number))
    if account is None or account.user_id != user.id:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


def deposit(db: Session, account: Account, amount: Decimal) -> Transaction:
    paise = to_paise(amount)
    txn = Transaction(to_account=account.account_number, amount=paise, type="deposit")
    db.add(txn)
    db.flush()
    db.add(LedgerEntry(transaction_id=txn.id, account_id=account.id, entry_type="credit", amount=paise))
    account.balance += paise
    db.commit()
    return txn


def withdraw(db: Session, account: Account, amount: Decimal) -> Transaction:
    paise = to_paise(amount)
    if account.balance < paise:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    txn = Transaction(from_account=account.account_number, amount=paise, type="withdraw")
    db.add(txn)
    db.flush()
    db.add(LedgerEntry(transaction_id=txn.id, account_id=account.id, entry_type="debit", amount=paise))
    account.balance -= paise
    db.commit()
    return txn


def transfer(db: Session, user: User, from_number: str, to_number: str, amount: Decimal,
             note: str | None = None, idempotency_key: str | None = None) -> Transaction:
    if idempotency_key:
        old = db.scalar(select(Transaction).where(Transaction.idempotency_key == idempotency_key))
        if old is not None:
            return old

    source = get_own_account(db, user, from_number)
    target = db.scalar(select(Account).where(Account.account_number == to_number))
    if target is None:
        raise HTTPException(status_code=404, detail="Recipient account not found")
    if source.id == target.id:
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account")

    paise = to_paise(amount)
    if source.balance < paise:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    try:
        txn = Transaction(from_account=from_number, to_account=to_number, amount=paise,
                          type="transfer", note=note, idempotency_key=idempotency_key)
        db.add(txn)
        db.flush()
        db.add(LedgerEntry(transaction_id=txn.id, account_id=source.id, entry_type="debit", amount=paise))
        db.add(LedgerEntry(transaction_id=txn.id, account_id=target.id, entry_type="credit", amount=paise))
        source.balance -= paise
        target.balance += paise
        db.commit()
    except Exception:
        db.rollback()
        raise
    return txn
