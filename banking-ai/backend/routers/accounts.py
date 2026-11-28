from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Account, Beneficiary, User
from ..schemas import AccountOut, BeneficiaryCreate, BeneficiaryOut
from ..security import get_current_user
from ..services.banking import get_own_account, new_account_number, to_rupees

router = APIRouter(prefix="/accounts", tags=["accounts"])


def account_out(account: Account) -> AccountOut:
    return AccountOut(account_number=account.account_number, account_type=account.account_type,
                      balance=to_rupees(account.balance), currency=account.currency)


@router.get("", response_model=list[AccountOut])
def my_accounts(user: User = Depends(get_current_user)):
    return [account_out(a) for a in user.accounts]


@router.post("", response_model=AccountOut)
def open_account(account_type: str = "savings", user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    account = Account(user_id=user.id, account_number=new_account_number(db), account_type=account_type)
    db.add(account)
    db.commit()
    return account_out(account)


@router.get("/beneficiaries", response_model=list[BeneficiaryOut])
def list_beneficiaries(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(select(Beneficiary).where(Beneficiary.user_id == user.id)).all()


@router.post("/beneficiaries", response_model=BeneficiaryOut)
def add_beneficiary(data: BeneficiaryCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if db.scalar(select(Account).where(Account.account_number == data.account_number)) is None:
        raise HTTPException(status_code=404, detail="No account with this number")
    beneficiary = Beneficiary(user_id=user.id, name=data.name, account_number=data.account_number)
    db.add(beneficiary)
    db.commit()
    return beneficiary


@router.get("/{account_number}", response_model=AccountOut)
def account_details(account_number: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return account_out(get_own_account(db, user, account_number))
