from fastapi import APIRouter, Depends

from drivers.dependencies import get_repository
from drivers.routers.users import connected_user
from adapters.ports.category_repository import CategoryRepository
from entities.category import Category
from entities.user import User

router = APIRouter(prefix="/categories")


@router.get("")
def categories_list(
    user:User = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    return category_repo.read(user_id=user.id)


@router.get("/{category_id}")
def category(
    category_id:str,
    user:User = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    return category_repo.read(user_id=user.id, id=category_id)[0]

@router.post("", status_code=201)
def create_category(
    item: Category,
    user = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    """Create a new category (owned by authenticated user)"""
    item.user_id = user.id
    return category_repo.create(item)


@router.put("/{category_id}")
def update_category(
    category_id:str,
    item: Category,
    user:User = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    item.user_id = user.id
    return category_repo.update(category_id, **item.model_dump(exclude_unset=True))


@router.delete("/{category_id}")
def delete_category(
    category_id:str,
    user:User = Depends(connected_user),
    category_repo: CategoryRepository = Depends(get_repository("category")),
):
    item = category_repo.read(user_id=user.id, id=category_id)[0]
    return category_repo.delete(**item.model_dump(exclude_unset=True))