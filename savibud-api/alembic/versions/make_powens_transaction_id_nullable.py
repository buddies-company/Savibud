"""Allow null powens_transaction_id on transactions."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "make_powens_txn_id_nullable"
down_revision: Union[str, Sequence[str], None] = "add_default_uuid_categories"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make powens_transaction_id nullable so legacy/manual inserts can omit it."""
    op.alter_column(
        "transactions",
        "powens_transaction_id",
        existing_type=sa.String(),
        nullable=True,
    )


def downgrade() -> None:
    """Revert powens_transaction_id to non-nullable."""
    op.alter_column(
        "transactions",
        "powens_transaction_id",
        existing_type=sa.String(),
        nullable=False,
    )
