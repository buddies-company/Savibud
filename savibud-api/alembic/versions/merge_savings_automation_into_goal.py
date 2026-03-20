"""Merge SavingsAutomation into SavingsGoal entity."""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'merge_savings_automation'
down_revision = 'add_icon_color_to_savings'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Migrate automation fields from savings_automations to savings_goals table."""
    # Add new columns to savings_goals
    op.add_column('savings_goals', sa.Column('automation_amount', sa.Numeric(precision=12, scale=2), nullable=True))
    op.add_column('savings_goals', sa.Column('automation_frequency', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True))
    op.add_column('savings_goals', sa.Column('automation_next_run_date', sa.Date(), nullable=True))
    op.add_column('savings_goals', sa.Column('automation_is_active', sa.Boolean(), nullable=False, server_default=sa.text('false')))
    
    # Migrate data from savings_automations to savings_goals
    op.execute("""
        UPDATE savings_goals
        SET 
            automation_amount = sa.amount,
            automation_frequency = sa.frequency,
            automation_next_run_date = sa.next_run_date,
            automation_is_active = sa.is_active
        FROM savings_automations sa
        WHERE savings_goals.id = sa.goal_id
    """)
    
    # Drop the savings_automations table
    op.drop_table('savings_automations')


def downgrade() -> None:
    """Restore savings_automations table and remove merged columns."""
    # Recreate savings_automations table
    op.create_table(
        'savings_automations',
        sa.Column('id', sa.Uuid(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('goal_id', sa.Uuid(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('frequency', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('next_run_date', sa.Date(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['goal_id'], ['savings_goals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Migrate data back from savings_goals to savings_automations
    op.execute("""
        INSERT INTO savings_automations (goal_id, amount, frequency, next_run_date, is_active)
        SELECT id, automation_amount, automation_frequency, automation_next_run_date, automation_is_active
        FROM savings_goals
        WHERE automation_amount IS NOT NULL
    """)
    
    # Remove merged columns from savings_goals
    op.drop_column('savings_goals', 'automation_amount')
    op.drop_column('savings_goals', 'automation_frequency')
    op.drop_column('savings_goals', 'automation_next_run_date')
    op.drop_column('savings_goals', 'automation_is_active')
