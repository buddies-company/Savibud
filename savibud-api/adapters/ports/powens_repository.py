from abc import ABC

from adapters.ports.crud import CRUD
from entities.powens import PowensConnection


class PowensRepository(CRUD[PowensConnection], ABC):
    """Repository to handle powenss"""
