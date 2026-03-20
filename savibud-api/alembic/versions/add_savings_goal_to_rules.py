"""Add savings_goal_id to rules and make category_id optional."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_savings_goal_to_rules'
down_revision = 'merge_budget_into_category'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Make category_id nullable
    op.alter_column('rules', 'category_id',
               existing_type=sa.UUID(),
               nullable=True)

    # Add savings_goal_id column
    op.add_column('rules', sa.Column('savings_goal_id', sa.UUID(), nullable=True))
    op.create_foreign_key('fk_rules_savings_goal_id', 'rules', 'savings_goals', ['savings_goal_id'], ['id'])

def downgrade() -> None:
    # Drop foreign key
    op.drop_constraint('fk_rules_savings_goal_id', 'rules', type_='foreignkey')

    # Remove savings_goal_id column
    op.drop_column('rules', 'savings_goal_id')

    # Make category_id non-nullable again
    op.alter_column('rules', 'category_id',
               existing_type=sa.UUID(),
               nullable=False)
