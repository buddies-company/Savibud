from sqlmodel import Session, select

from adapters.ports.rule_repository import (
    RuleRepository as RuleRepositoryBase,
)
from adapters.postgres.crud import CRUD
from entities.rule import Rule


class RuleRepository(RuleRepositoryBase, CRUD):
    """Rule Repository using Postgres (SQLModel) data"""

    def __init__(self, session: Session):
        super().__init__(session, Rule)
