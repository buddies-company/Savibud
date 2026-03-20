from fastapi import APIRouter, Depends

from adapters.ports.category_repository import CategoryRepository
from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from entities.category import Category
from entities.user import User
from datetime import date, datetime
import calendar

router = APIRouter(prefix="/categories")


@router.get("")
def categories_list(
    user: User = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    return category_repo.read(user_id=user.id)


@router.get("/{category_id}")
def category(
    category_id: str,
    user: User = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    result = category_repo.read(user_id=user.id, id=category_id)
    return result[0] if result else None


@router.post("", status_code=201)
def create_category(
    item: Category,
    user=Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    """Create a new category (owned by authenticated user)"""
    item.user_id = user.id
    return category_repo.create(item)


@router.put("/{category_id}")
def update_category(
    category_id: str,
    item: Category,
    user: User = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    item.user_id = user.id
    return category_repo.update(category_id, **item.model_dump(exclude_unset=True))


@router.delete("/{category_id}")
def delete_category(
    category_id: str,
    user: User = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    result = category_repo.read(user_id=user.id, id=category_id)
    if result:
        return category_repo.delete(result[0])
    return {"error": "Not found"}

@router.get("/stats/budget")
def get_budget_planning_stats(
    month: str,  # Expected format YYYY-MM
    user: User = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    # Parse the YYYY-MM string
    dt = datetime.strptime(month, "%Y-%m")
    last_day = calendar.monthrange(dt.year, dt.month)[1]
    
    start_date = date(dt.year, dt.month, 1)
    end_date = date(dt.year, dt.month, last_day)
    
    return category_repo.get_budget_stats(user.id, start_date, end_date)