from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query

from adapters.ports.saving_repository import SavingsGoalRepository
from adapters.ports.transaction_repository import TransactionRepository
from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from entities.transaction import TransactionReadWithCategory, Transaction
from entities.user import User
from use_cases.transactions import TransactionInteractor
from use_cases.recalculate_savings import RecalculateSavingsGoals

router = APIRouter(prefix="/transactions")


@router.get("", response_model=list[TransactionReadWithCategory])
def transactions_list(
    user: User = Depends(connected_user),
    transaction_repo: TransactionRepository = Depends(get_repository("transaction")),
    q: Optional[str] = Query(None),
    account_id: Optional[UUID] = Query(None),
    category_id: Optional[UUID] = Query(None),
    savings_goal_id: Optional[UUID] = Query(None),
    date_from: Optional[str] = Query(None, description="ISO format date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="ISO format date (YYYY-MM-DD)"),
    uncategorized_only: bool = Query(False, description="Show only uncategorized transactions"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    interactor = TransactionInteractor(transaction_repo)
    return interactor.list_transactions(
        user_id=user.id,
        q=q,
        account_id=account_id,
        category_id=category_id,
        savings_goal_id=savings_goal_id,
        date_from=date_from,
        date_to=date_to,
        uncategorized_only=uncategorized_only,
        limit=limit,
        offset=(page - 1) * limit
    )

@router.post("/{transaction_id}/toggle_internal")
def toggle_internal(
    transaction_id: int,
    user: User = Depends(connected_user),
    transaction_repo: TransactionRepository = Depends(get_repository("transaction")),
):
    interactor = TransactionInteractor(transaction_repo)
    updated_tx = interactor.toggle_internal_status(transaction_id, user.id)
    
    if not updated_tx:
        return {"error": "Transaction not found or access denied"}
        
    return updated_tx


@router.post("", status_code=201)
def create_transaction(
    item: Transaction,
    user: User = Depends(connected_user),
    transaction_repo: TransactionRepository = Depends(get_repository("transaction")),
    savings_repo: SavingsGoalRepository = Depends(get_repository("saving_goals")),
):

    interactor = TransactionInteractor(transaction_repo)
    try:
        created = interactor.create_transaction(user.id, item)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    # Recalculate savings goals if transaction is linked to one
    if created.savings_goal_id:
        recalculator = RecalculateSavingsGoals(savings_repo, transaction_repo)
        recalculator(user.id)
    
    return created


@router.put("/{transaction_id}")
def update_transaction(
    transaction_id: int,
    item: Transaction,
    user: User = Depends(connected_user),
    transaction_repo: TransactionRepository = Depends(get_repository("transaction")),
    savings_repo: SavingsGoalRepository = Depends(get_repository("saving_goals")),
):
    interactor = TransactionInteractor(transaction_repo)
    modifications = item.model_dump(exclude_unset=True)
    
    # Get the current transaction to check if savings_goal_id changed
    current_tx = transaction_repo.get_by_id_and_user(transaction_id, user.id)
    old_savings_goal_id = current_tx.savings_goal_id if current_tx else None
    
    try:
        updated = interactor.update_transaction(transaction_id, user.id, **modifications)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    if not updated:
        return {"error": "Transaction not found or access denied"}
    
    # Recalculate savings goals if savings_goal_id changed
    new_savings_goal_id = updated.savings_goal_id
    if old_savings_goal_id != new_savings_goal_id:
        recalculator = RecalculateSavingsGoals(savings_repo, transaction_repo)
        recalculator(user.id)
    
    return updated