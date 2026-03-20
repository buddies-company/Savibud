from typing import Any, Generic, List, Type, TypeVar, Optional

from sqlmodel import Session, SQLModel, asc, desc, select

from adapters.ports.crud import CRUD as CRUDBase, T

# bound=SQLModel means T must be a SQLModel or a subclass of it
T = TypeVar("T", bound=SQLModel)


class CRUD(CRUDBase[T]):
    """Generic CRUD Repository using PostgreSQL and SQLModel"""

    def __init__(self, session: Session, model: Type[T]):
        self.session = session
        self.model = model

    def read(self, **filters) -> List[T]:
        statement = select(self.model)

        if "limit" in filters:
            statement = statement.limit(filters.pop("limit"))
        if "offset" in filters:
            statement = statement.offset(filters.pop("offset"))
        
        if "sort_by" in filters:
            sort_col = filters.pop("sort_by")
            order = filters.pop("order", "asc").lower()
            col_attr = getattr(self.model, sort_col, None)
            if col_attr:
                statement = statement.order_by(desc(col_attr) if order == "desc" else asc(col_attr))

        for key, value in filters.items():
            if hasattr(self.model, key):
                statement = statement.where(getattr(self.model, key) == value)

        return list(self.session.exec(statement).all())


    def create(self, element: T) -> T:
        """Implement create logic"""
        self.session.add(element)
        self.session.commit()
        self.session.refresh(element)
        return element

    def update(self, item_id: Any, **modifications) -> Optional[T]:
        """Update logic to handle partial updates cleanly"""
        item = self.session.get(self.model, item_id)
        if not item:
            return None

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

    def upsert(self, element: T, **filters) -> T:
        statement = select(self.model)
        for key, value in filters.items():
            statement = statement.where(getattr(self.model, key) == value)
        
        existing = self.session.exec(statement).first()

        if existing:
            update_data = element.model_dump(exclude_unset=True, exclude_none=True)
            update_data.pop("id", None) 

            for key, value in update_data.items():
                if hasattr(existing, key):
                    setattr(existing, key, value)
            
            self.session.add(existing)
            self.session.commit()
            self.session.refresh(existing)
            return existing
        else:
            self.session.add(element)
            self.session.commit()
            self.session.refresh(element)
            return element