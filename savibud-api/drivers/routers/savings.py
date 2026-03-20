"""Savings Goals API endpoints."""
from datetime import date as date_type
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from adapters.ports.saving_repository import SavingsGoalRepository
from adapters.ports.transaction_repository import TransactionRepository
from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from entities.saving import SavingsGoal
from entities.transaction import Transaction
from entities.user import User

router = APIRouter(prefix="/savings_goals", tags=["savings"])


@router.get("")
def list_savings_goals(
    user: User = Depends(connected_user),
    repo: SavingsGoalRepository = Depends(get_repository("saving_goals")),
) -> list[SavingsGoal]:
    """List all savings goals for the authenticated user."""
    return repo.read(user_id=user.id)


@router.post("")
def create_savings_goal(
    goal: SavingsGoal,
    user: User = Depends(connected_user),
    repo: SavingsGoalRepository = Depends(get_repository("saving_goals")),
) -> SavingsGoal:
    """Create a new savings goal."""
    goal.user_id = user.id
    return repo.create(goal)


@router.get("/{goal_id}")
def get_savings_goal(
    goal_id: str,
    user: User = Depends(connected_user),
    repo: SavingsGoalRepository = Depends(get_repository("saving_goals")),
) -> SavingsGoal:
    """Get a specific savings goal."""
    goals = repo.read(id=goal_id, user_id=user.id)
    if not goals:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    return goals[0]


@router.put("/{goal_id}")
def update_savings_goal(
    goal_id: str,
    goal_data: dict,
    user: User = Depends(connected_user),
    repo: SavingsGoalRepository = Depends(get_repository("saving_goals")),
) -> SavingsGoal:
    """Update a savings goal."""
    # Verify ownership
    goals = repo.read(id=goal_id, user_id=user.id)
    if not goals:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    # Update only allowed fields
    allowed_fields = {"label", "target_amount", "current_amount"}
    update_data = {k: v for k, v in goal_data.items() if k in allowed_fields}
    
    return repo.update(goal_id, **update_data)


@router.delete("/{goal_id}")
def delete_savings_goal(
    goal_id: str,
    user: User = Depends(connected_user),
    repo: SavingsGoalRepository = Depends(get_repository("saving_goals")),
) -> dict:
    """Delete a savings goal."""
    goals = repo.read(id=goal_id, user_id=user.id)
    if not goals:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    repo.delete(goals[0])
    return {"status": "deleted"}


@router.post("/{goal_id}/contribute")
def contribute_to_goal(
    goal_id: str,
    contribution: dict,  # {"amount": float, "label": str, "date": str (optional)}
    user: User = Depends(connected_user),
    goal_repo: SavingsGoalRepository = Depends(get_repository("saving_goals")),
    transaction_repo: TransactionRepository = Depends(get_repository("transaction")),
) -> Transaction:
    """Contribute to a savings goal by creating a virtual transaction.
    
    Creates a new transaction linked to the savings goal without an associated account
    or Powens transaction ID. This transaction represents the user's contribution.
    """
    # Verify goal exists and belongs to user
    goals = goal_repo.read(id=goal_id, user_id=user.id)
    if not goals:
        raise HTTPException(status_code=404, detail="Savings goal not found")
    
    goal = goals[0]
    amount = contribution.get("amount", 0)
    label = contribution.get("label", f"Contribution to {goal.name}")
    date = contribution.get("date", date_type.today().isoformat())
    
    # Create virtual transaction
    virtual_tx = Transaction(
        user_id=user.id,
        savings_goal_id=goal_id,
        amount=Decimal(str(amount)),
        label=label,
        date=date_type.fromisoformat(date),
        is_internal=True,  # Mark as internal/virtual transaction
    )
    
    return transaction_repo.create(virtual_tx)
