"""Merge Budget into Category entity

Revision ID: merge_budget_into_category
Revises: add_rules_table
Create Date: 2026-02-06 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "merge_budget_into_category"
down_revision: Union[str, Sequence[str], None] = "add_rules_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to categories table (from budgets)
    op.add_column("categories", sa.Column("budget_amount", sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column("categories", sa.Column("budget_period", sa.String(length=20), nullable=False, server_default="monthly"))
    op.add_column("categories", sa.Column("budget_start_date", sa.Date(), nullable=True))
    op.add_column("categories", sa.Column("budget_end_date", sa.Date(), nullable=True))
    op.add_column("categories", sa.Column("is_fixed", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    # Drop the budgets table (assuming budgets data was already migrated)
    # Note: If you need to preserve budget data, copy it to categories first
    op.drop_table("budgets")


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate budgets table
    op.create_table(
        "budgets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("period", sa.String(length=20), nullable=False, server_default="monthly"),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_fixed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Remove new columns from categories
    op.drop_column("categories", "is_fixed")
    op.drop_column("categories", "budget_end_date")
    op.drop_column("categories", "budget_start_date")
    op.drop_column("categories", "budget_period")
    op.drop_column("categories", "budget_amount")
