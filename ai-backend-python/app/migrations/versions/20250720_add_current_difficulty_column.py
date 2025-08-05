from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250720_add_current_difficulty_column'
down_revision = '20250715_add_agentmetrics_leveling'
branch_labels = None
depends_on = None

def upgrade():
    # Add current_difficulty column to agent_metrics table
    op.add_column('agent_metrics', sa.Column('current_difficulty', sa.String(50), nullable=True, server_default='basic'))
    
    # Update existing records to have the default value
    op.execute("UPDATE agent_metrics SET current_difficulty = 'basic' WHERE current_difficulty IS NULL")

def downgrade():
    # Remove current_difficulty column from agent_metrics table
    op.drop_column('agent_metrics', 'current_difficulty') 