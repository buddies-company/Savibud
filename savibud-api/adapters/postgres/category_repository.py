from adapters.ports.category_repository import (
    CategoryRepository as CategoryRepositoryBase,
)
from adapters.postgres.crud import CRUD
from entities.category import Category


class CategoryRepository(CategoryRepositoryBase, CRUD):
    """Category Repository using Postgres (SQLModel) data"""

    def __init__(self, session):
        super().__init__(session, Category)