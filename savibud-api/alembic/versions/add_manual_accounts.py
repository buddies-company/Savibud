"""Add manual accounts support to existing snapshot_accounts table."""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'add_manual_accounts'
down_revision = 'merge_savings_automation'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create manual_accounts table and enhance snapshot_accounts table."""
    # Create manual_accounts table
    op.create_table(
        'manual_accounts',
        sa.Column('id', sa.Uuid(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('account_type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('current_balance', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('currency', sqlmodel.sql.sqltypes.AutoString(length=3), nullable=False, server_default='EUR'),
        sa.Column('loan_initial_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('loan_interest_rate', sa.Numeric(precision=5, scale=3), nullable=True),
        sa.Column('loan_duration_months', sa.Integer(), nullable=True),
        sa.Column('loan_start_date', sa.Date(), nullable=True),
        sa.Column('loan_monthly_payment', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('icon', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True, server_default='BanknotesIcon'),
        sa.Column('color', sqlmodel.sql.sqltypes.AutoString(length=7), nullable=False, server_default='#3b82f6'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Enhance existing snapshot_accounts table to support both Powens and manual accounts
    # Add user_id column
    op.add_column('snapshot_accounts', sa.Column('user_id', sa.Uuid(), nullable=True))
    
    # Add recorded_at column
    op.add_column('snapshot_accounts', sa.Column('recorded_at', sa.DateTime(), nullable=True, server_default=sa.func.now()))
    
    # Add manual_account_id column for manual account snapshots
    op.add_column('snapshot_accounts', sa.Column('manual_account_id', sa.Uuid(), nullable=True))
    
    # Make account_id nullable to support manual accounts
    op.alter_column('snapshot_accounts', 'account_id', existing_type=sa.Uuid(), nullable=True)
    
    # Add foreign key constraint for manual_account_id
    op.create_foreign_key(
        'fk_snapshot_accounts_manual_account_id',
        'snapshot_accounts',
        'manual_accounts',
        ['manual_account_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Add check constraint to ensure one of the two accounts is set
    op.create_check_constraint(
        'ck_snapshot_accounts_account_source',
        'snapshot_accounts',
        '(account_id IS NOT NULL OR manual_account_id IS NOT NULL)'
    )
    
    # Backfill user_id for existing Powens snapshots
    op.execute("""
        UPDATE snapshot_accounts ss
        SET user_id = a.user_id
        FROM accounts a
        WHERE ss.account_id = a.id AND ss.user_id IS NULL
    """)
    
    # Make user_id non-nullable after backfill
    op.alter_column('snapshot_accounts', 'user_id', existing_type=sa.Uuid(), nullable=False)
    
    # Make recorded_at non-nullable
    op.alter_column('snapshot_accounts', 'recorded_at', existing_type=sa.DateTime(), nullable=False)


def downgrade() -> None:
    """Revert changes."""
    # Drop check constraint
    op.drop_constraint('ck_snapshot_accounts_account_source', 'snapshot_accounts')
    
    # Drop foreign key for manual_account_id
    op.drop_constraint('fk_snapshot_accounts_manual_account_id', 'snapshot_accounts')
    
    # Remove manual_account_id column
    op.drop_column('snapshot_accounts', 'manual_account_id')
    
    # Remove recorded_at column
    op.drop_column('snapshot_accounts', 'recorded_at')
    
    # Remove user_id column
    op.drop_column('snapshot_accounts', 'user_id')
    
    # Revert account_id to non-nullable
    op.alter_column('snapshot_accounts', 'account_id', existing_type=sa.Uuid(), nullable=False)
    op.drop_table('account_snapshots')
    op.drop_table('manual_accounts')
