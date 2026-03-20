"""Abstract Rule repository interface."""

from abc import ABC

from entities.rule import Rule
from adapters.ports.crud import CRUD


class RuleRepository(CRUD[Rule], ABC):
    """Abstract repository for Rules."""