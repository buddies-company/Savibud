"""Add default UUID generation to savings_goals.id."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_default_uuid_savings_goals"
down_revision: Union[str, Sequence[str], None] = "merge_add_unique_user_goal_name"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure savings_goals.id auto-generates a UUID."""
    op.alter_column(
        "savings_goals",
        "id",
        existing_type=sa.Uuid(),
        nullable=False,
        server_default=sa.text("gen_random_uuid()"),
    )


def downgrade() -> None:
    """Revert auto-generation of UUID on savings_goals.id."""
    op.alter_column(
        "savings_goals",
        "id",
        existing_type=sa.Uuid(),
        nullable=False,
        server_default=None,
    )
