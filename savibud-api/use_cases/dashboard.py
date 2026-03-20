from dataclasses import dataclass
from uuid import UUID

from adapters.ports.saving_repository import SavingsGoalRepository


@dataclass
class TopGoals:
    savings: SavingsGoalRepository

    def __call__(self, user_id: UUID):
        return self.savings.read(
            user_id=user_id, limit=3, sort_by="target_amount", order="desc"
        )
