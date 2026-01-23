from abc import ABC

from adapters.ports.crud import CRUD
from entities.category import Category


class CategoryRepository(CRUD[Category], ABC):
    """Repository to handle categories"""