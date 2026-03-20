"""Add default UUID generation to categories.id."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_default_uuid_categories"
down_revision: Union[str, Sequence[str], None] = "add_default_uuid_savings_goals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Ensure categories.id auto-generates UUIDs."""
    op.alter_column(
        "categories",
        "id",
        existing_type=sa.Uuid(),
        nullable=False,
        server_default=sa.text("gen_random_uuid()"),
    )


def downgrade() -> None:
    """Revert auto-generation of UUID on categories.id."""
    op.alter_column(
        "categories",
        "id",
        existing_type=sa.Uuid(),
        nullable=False,
        server_default=None,
    )
