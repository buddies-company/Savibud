"""Add rules table for automatic categorization

Revision ID: add_rules_table
Revises: 9cb5d4e2cd5b
Create Date: 2026-02-05 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_rules_table"
down_revision: Union[str, Sequence[str], None] = "9cb5d4e2cd5b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create rules table
    op.create_table(
        "rules",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("keywords", JSON(), nullable=True),
        sa.Column("regex_pattern", sa.String(length=255), nullable=True),
        sa.Column("min_amount", sa.Float(), nullable=True),
        sa.Column("max_amount", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("priority", sa.Integer(), nullable=False, server_default=sa.text("100")),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_rules_user_id", "user_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("rules")
