"""Add icon and color to savings goals."""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_icon_color_to_savings'
down_revision = 'add_savings_goal_to_rules'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add icon column with default
    op.add_column('savings_goals', sa.Column('icon', sa.String(length=100), nullable=True))
    
    # Add color column with default
    op.add_column('savings_goals', sa.Column('color', sa.String(length=7), nullable=False, server_default='#3b82f6'))
    
    # Set default for existing rows
    op.execute("UPDATE savings_goals SET icon = 'BanknotesIcon' WHERE icon IS NULL")


def downgrade() -> None:
    # Remove columns
    op.drop_column('savings_goals', 'color')
    op.drop_column('savings_goals', 'icon')
