from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Transaction, User
from ..schemas import MoneyIn, TransactionOut, TransferIn
from ..security import get_current_user
from ..services import banking

router = APIRouter(prefix="/transactions", tags=["transactions"])


def txn_out(txn: Transaction) -> TransactionOut:
    return TransactionOut(id=txn.id, from_account=txn.from_account, to_account=txn.to_account,
                          amount=banking.to_rupees(txn.amount), type=txn.type, status=txn.status,
                          note=txn.note, created_at=txn.created_at)


@router.post("/deposit", response_model=TransactionOut)
def deposit(data: MoneyIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = banking.get_own_account(db, user, data.account_number)
    return txn_out(banking.deposit(db, account, data.amount))


@router.post("/withdraw", response_model=TransactionOut)
def withdraw(data: MoneyIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = banking.get_own_account(db, user, data.account_number)
    return txn_out(banking.withdraw(db, account, data.amount))


@router.post("/transfer", response_model=TransactionOut)
def transfer(data: TransferIn, idempotency_key: str | None = Header(default=None),
             user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txn = banking.transfer(db, user, data.from_account, data.to_account, data.amount,
                           note=data.note, idempotency_key=idempotency_key)
    return txn_out(txn)


@router.get("", response_model=list[TransactionOut])
def history(limit: int = 20, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    numbers = [a.account_number for a in user.accounts]
    query = (select(Transaction)
             .where(or_(Transaction.from_account.in_(numbers), Transaction.to_account.in_(numbers)))
             .order_by(Transaction.id.desc()).limit(limit))
    return [txn_out(t) for t in db.scalars(query)]


@router.get("/{txn_id}", response_model=TransactionOut)
def details(txn_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    txn = db.get(Transaction, txn_id)
    numbers = [a.account_number for a in user.accounts]
    if txn is None or (txn.from_account not in numbers and txn.to_account not in numbers):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn_out(txn)
