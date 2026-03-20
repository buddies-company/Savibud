"""Merge heads and add unique constraint to savings_goals."""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "merge_add_unique_user_goal_name"
down_revision: Union[str, Sequence[str], None] = ("add_manual_accounts", "b1e0a54db937")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add unique constraint to allow ON CONFLICT on (user_id, name)."""
    op.create_unique_constraint(
        "unique_user_goal_name",
        "savings_goals",
        ["user_id", "name"],
    )


def downgrade() -> None:
    """Remove unique constraint."""
    op.drop_constraint("unique_user_goal_name", "savings_goals", type_="unique")
