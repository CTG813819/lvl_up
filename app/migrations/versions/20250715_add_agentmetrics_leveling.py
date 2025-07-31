from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250715_add_agentmetrics_leveling'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('agent_metrics', sa.Column('xp', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('agent_metrics', sa.Column('level', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('agent_metrics', sa.Column('prestige', sa.Integer(), nullable=True, server_default='0'))

def downgrade():
    op.drop_column('agent_metrics', 'xp')
    op.drop_column('agent_metrics', 'level')
    op.drop_column('agent_metrics', 'prestige') 