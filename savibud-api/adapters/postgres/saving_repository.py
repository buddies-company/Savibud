from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlmodel import Session, and_, func, select

from adapters.ports.saving_repository import (
    SavingsGoalRepository as SavingsGoalRepositoryInterface,
)
from adapters.postgres.crud import CRUD
from entities.saving import SavingsGoal
from entities.transaction import Transaction


class SavingsGoalRepository(SavingsGoalRepositoryInterface, CRUD[SavingsGoal]):
    """Savings Goal postgres repository (includes automation functionality)"""

    def __init__(self, session: Session):
        super().__init__(session, SavingsGoal)

    def sum_target_amount(self, user_id):
        budget_stmt = select(func.sum(SavingsGoal.target_amount)).where(
            and_(
                SavingsGoal.user_id == user_id,
            )
        )
        return self.session.exec(budget_stmt).one() or Decimal(0)

    def upsert_account(self, user_id: UUID, account_data: dict):
        """Insert or update a savings goal for the user."""
        statement = select(SavingsGoal).where(
            SavingsGoal.user_id == user_id, SavingsGoal.name == account_data["name"]
        )
        goal = self.session.exec(statement).first()

        if goal:
            # Update existing goal
            goal.target_amount = Decimal(
                account_data.get("target_amount", goal.target_amount)
            )
            self.session.add(goal)
        else:
            # Create new goal
            new_goal = SavingsGoal(
                user_id=user_id,
                name=account_data["name"],
                target_amount=Decimal(account_data.get("target_amount", 0.00)),
                current_amount=Decimal(account_data.get("current_amount", 0.00)),
            )
            self.session.add(new_goal)

    def get_due_automations(self, as_of_date: date) -> list[SavingsGoal]:
        """Fetch all active automations that need to run today or earlier."""
        statement = select(SavingsGoal).where(
            SavingsGoal.automation_is_active == True,
            SavingsGoal.automation_next_run_date <= as_of_date,
        )
        return list(self.session.exec(statement).all())

    def create_virtual_transaction(self, goal_id: UUID, amount: Decimal, label: str):
        """Creates the virtual record and updates the goal's current amount."""
        # 1. Add the transaction
        transaction = Transaction(amount=amount, label=label, savings_goal_id=goal_id)
        self.session.add(transaction)

        # 2. Update the actual goal balance
        statement = select(SavingsGoal).where(SavingsGoal.id == goal_id)
        goal = self.session.exec(statement).one()
        goal.current_amount += amount

        self.session.add(goal)
        # We don't commit yet; the Use Case or Driver should handle the commit
        # to ensure all steps succeed together (atomicity).

    def update_automation_date(self, goal_id: UUID, new_date: date):
        """Updates the automation schedule for the next run."""
        statement = select(SavingsGoal).where(SavingsGoal.id == goal_id)
        goal = self.session.exec(statement).one()
        goal.automation_next_run_date = new_date
        self.session.add(goal)

