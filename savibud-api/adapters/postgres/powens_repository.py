from adapters.ports.powens_repository import PowensRepository as PowensRepositoryBase
from adapters.postgres.crud import CRUD
from entities.powens import PowensConnection


class PowensRepository(PowensRepositoryBase, CRUD[PowensConnection]):
    """Powens Repository using Postgres (SQLModel) data"""

    def __init__(self, session):
        super().__init__(session, PowensConnection)
