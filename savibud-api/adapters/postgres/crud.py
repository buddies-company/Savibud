from typing import Any, Generic, List, Type, TypeVar

from sqlmodel import Session, SQLModel, asc, desc, select

from adapters.ports.crud import CRUD as CRUDBase
from adapters.ports.crud import T

# bound=SQLModel means T must be a SQLModel or a subclass of it
T = TypeVar("T", bound=SQLModel)


class CRUD(CRUDBase[T]):
    """Generic CRUD Repository using PostgreSQL and SQLModel"""

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def read(self, **filters):
        statement = select(self.model)

        if "limit" in filters:
            limit_value = filters.pop("limit")
            statement = statement.limit(limit_value)

        if "offset" in filters:
            offset_value = filters.pop("offset")
            statement = statement.offset(offset_value)

        if "sort_by" in filters:
            sort_column = filters.pop("sort_by")
            sort_order = filters.pop("order", "asc").lower()

            if hasattr(self.model, sort_column):
                column_attr = getattr(self.model, sort_column)
                if sort_order == "desc":
                    statement = statement.order_by(desc(column_attr))
                else:
                    statement = statement.order_by(asc(column_attr))

        for key, value in filters.items():
            # Dynamically apply filters based on model attributes
            if hasattr(self.model, key):
                statement = statement.where(getattr(self.model, key) == value)

        results = self.session.exec(statement).all()
        return list(results)

    def create(self, element: T) -> T:
        """Implement create logic"""
        self.session.add(element)
        self.session.commit()
        self.session.refresh(element)
        return element

    def update(self, item_id: Any, **modifications):
        """Implement update logic"""
        # 1. Fetch the existing item
        item = self.session.get(self.model, item_id)
        if not item:
            return None

        # 2. Apply modifications
        for key, value in modifications.items():
            if hasattr(item, key):
                setattr(item, key, value)

        self.session.add(item)
        self.session.commit()
        self.session.refresh(item)
        return item

    def delete(self, item: T) -> bool:
        """Implement delete logic"""
        try:
            self.session.delete(item)
            self.session.commit()
            return True
        except Exception:
            self.session.rollback()
            return False
