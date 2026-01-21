"""add_snapshot_account

Revision ID: b1e0a54db937
Revises: ddab390f3019
Create Date: 2026-01-04 18:26:44.910373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1e0a54db937'
down_revision: Union[str, Sequence[str], None] = 'ddab390f3019'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
