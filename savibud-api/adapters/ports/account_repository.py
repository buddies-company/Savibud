from abc import ABC

from adapters.ports.crud import CRUD
from entities.account import Account, SnapshotAccount


class AccountRepository(CRUD[Account], ABC):
    """Repository to handle accounts"""

class SnapshotAccountRepository(CRUD[SnapshotAccount], ABC):
    """Repository to handle Snapshot accounts"""