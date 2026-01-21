from fastapi import APIRouter, Depends

from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from adapters.ports.budget_repository import BudgetRepository
from entities.budget import Budget, BudgetReadWithCategory
from entities.user import User

router = APIRouter(prefix="/budgets")


@router.get("",response_model=list[BudgetReadWithCategory])
def budgets_list(
    user= Depends(connected_user),
    budget_repo: BudgetRepository = Depends(get_repository("budget")),
):
    return budget_repo.read(user_id=user.id)

@router.get("/{budget_id}")
def budget(
    budget_id:str,
    user:User = Depends(connected_user),
    budget_repo: BudgetRepository = Depends(get_repository("budget")),
):
    return budget_repo.read(user_id=user.id, id=budget_id)[0]

@router.post("", status_code=201)
def create_budget(
    item: Budget,
    user = Depends(connected_user),
    budget_repo: BudgetRepository = Depends(get_repository("budget")),
):
    """Create a new budget (owned by authenticated user)"""
    item.user_id = user.id
    return budget_repo.create(item)


@router.put("/{budget_id}")
def update_budget(
    budget_id:str,
    item: Budget,
    user:User = Depends(connected_user),
    budget_repo: BudgetRepository = Depends(get_repository("budget")),
):
    item.user_id = user.id
    return budget_repo.update(budget_id, **item.model_dump(exclude_unset=True))


@router.delete("/{budget_id}")
def delete_budget(
    budget_id:str,
    user:User = Depends(connected_user),
    budget_repo: BudgetRepository = Depends(get_repository("budget")),
):
    item = budget_repo.read(user_id=user.id, id=budget_id)[0]
    return budget_repo.delete(**item.model_dump(exclude_unset=True))