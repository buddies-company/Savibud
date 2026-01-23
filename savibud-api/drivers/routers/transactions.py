from fastapi import APIRouter, Depends

from adapters.ports.account_repository import AccountRepository
from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from adapters.ports.transaction_repository import TransactionRepository
from entities.transaction import TransactionReadWithCategory

router = APIRouter(prefix="/transactions")

@router.get("",response_model=list[TransactionReadWithCategory])
def transactions_list(
    user= Depends(connected_user),
    transaction_repo: TransactionRepository = Depends(get_repository("transaction")),
):
    return transaction_repo.read(user_id=user.id)

acc_router = APIRouter(prefix="/accounts")

@acc_router.get("")
def accounts_list(
    user= Depends(connected_user),
    account_repo: AccountRepository = Depends(get_repository("account")),
):
    return account_repo.read(user_id=user.id)