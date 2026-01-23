"""add_user_id_to_transactions

Revision ID: ddab390f3019
Revises: a2e85295766a
Create Date: 2026-01-02 12:31:01.766003

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddab390f3019'
down_revision: Union[str, Sequence[str], None] = 'a2e85295766a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add the user_id column as nullable first
    op.add_column('transactions', sa.Column('user_id', sa.UUID(), nullable=True))
    op.add_column('budgets', sa.Column('start_date', sa.Date(), nullable=True))
    op.add_column('budgets', sa.Column('end_date', sa.Date(), nullable=True))

    # 2. Backfill: Update user_id by joining with accounts
    # This SQL finds the user_id from the linked account and copies it to the transaction
    op.execute("""
        UPDATE transactions
        SET user_id = accounts.user_id
        FROM accounts
        WHERE transactions.account_id = accounts.id
    """)

    # 3. Now that data is backfilled, make it NOT NULL and add Foreign Key
    op.alter_column('transactions', 'user_id', nullable=False)
    op.create_foreign_key(
        'fk_transactions_user_id', # Name of the constraint
        'transactions', 'users',   # Source table and target table
        ['user_id'], ['id'],       # Source col and target col
        ondelete='CASCADE'
    )

def downgrade() -> None:
    # Remove the constraint and the column
    op.drop_constraint('fk_transactions_user_id', 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'user_id')