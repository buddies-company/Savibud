"""Use case for recalculating savings goal amounts from transactions."""

from decimal import Decimal
from uuid import UUID

from adapters.ports.saving_repository import SavingsGoalRepository
from adapters.ports.transaction_repository import TransactionRepository


class RecalculateSavingsGoals:
    """Recalculate current amount for all savings goals based on linked transactions."""

    def __init__(self, savings_repo: SavingsGoalRepository, transaction_repo: TransactionRepository):
        self.savings_repo = savings_repo
        self.transaction_repo = transaction_repo

    def __call__(self, user_id: UUID) -> None:
        """
        Recalculate all savings goals for a user by summing their linked transactions.

        Args:
            user_id: The user whose savings goals should be recalculated
        """
        # Get all savings goals for the user
        goals = self.savings_repo.read(user_id=user_id)
        
        for goal in goals:
            # Get all transactions linked to this goal
            transactions = self.transaction_repo.read(savings_goal_id=goal.id)
            
            # Sum up the transaction amounts
            total = sum((Decimal(str(tx.amount)) for tx in transactions), Decimal(0))
            
            # Update the goal's current amount
            goal.current_amount = total
            self.savings_repo.update(goal.id, current_amount=total)
