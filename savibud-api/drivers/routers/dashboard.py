from datetime import datetime, timedelta

from fastapi import APIRouter, Depends

from adapters.ports.account_repository import AccountRepository, ManualAccountRepository
from adapters.ports.category_repository import CategoryRepository
from adapters.ports.saving_repository import SavingsGoalRepository
from adapters.ports.transaction_repository import TransactionRepository
from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from entities.user import User
from use_cases.dashboard import TopGoals

router = APIRouter(prefix="/dashboard")


def last_day_of_month(any_day: datetime):
    # The day 28 exists in every month. 4 days later, it's always next month
    next_month = any_day.replace(day=28) + timedelta(days=4)
    # subtracting the number of the current day brings us back one month
    return next_month - timedelta(days=next_month.day)


@router.get("/summary")
async def get_dashboard_summary(
    period_start: datetime = datetime.today().replace(day=1),
    period_end: datetime = last_day_of_month(datetime.today()),
    current_user: User = Depends(connected_user),
    savings_repo: SavingsGoalRepository = Depends(get_repository("saving_goals")),
    account_repo: AccountRepository = Depends(get_repository("account")),
    manual_account_repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
    category_repo: CategoryRepository = Depends(get_repository("category")),
    transaction_repo: TransactionRepository = Depends(get_repository("transaction")),
):
    # Total Balance
    accounts = account_repo.read(user_id=current_user.id)
    manual_accounts = manual_account_repo.read(user_id=current_user.id, type="manual")
    total_balance = sum(acc.balance for acc in accounts)
    total_balance += sum(acc.current_balance for acc in manual_accounts)

    total_budget = category_repo.sum_amount(current_user.id, period_start, period_end)
    total_budget_spent = category_repo.sum_amount_spent(
        current_user.id, period_start, period_end
    )
    upcoming_bills = category_repo.remaining_bills(
        current_user.id, period_start, period_end
    )

    # Monthly Savings Goals
    # Sum of the targets for the current month
    savings_targets = savings_repo.sum_target_amount(current_user.id)

    # Safe to Spend calculation
    safe_to_spend = total_balance - upcoming_bills - savings_targets
    goals = TopGoals(savings_repo)

    return {
        "total_balance": total_balance,
        "upcoming_bills": upcoming_bills,
        "safe_to_spend": safe_to_spend,
        "total_budget": total_budget,
        "total_budget_spent": total_budget_spent,
        "recent_activity": transaction_repo.read(user_id=current_user.id, limit=5),
        "goals": goals(current_user.id),
    }
