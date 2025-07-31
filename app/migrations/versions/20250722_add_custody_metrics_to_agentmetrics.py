"""
Add custody test fields to agent_metrics table

Revision ID: 20250722_add_custody_metrics_to_agentmetrics
Revises: 20250720_add_current_difficulty_column
Create Date: 2025-07-22
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250722_add_custody_metrics_to_agentmetrics'
down_revision = '20250720_add_current_difficulty_column'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('agent_metrics', sa.Column('total_tests_given', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('agent_metrics', sa.Column('total_tests_passed', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('agent_metrics', sa.Column('total_tests_failed', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('agent_metrics', sa.Column('consecutive_successes', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('agent_metrics', sa.Column('consecutive_failures', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('agent_metrics', sa.Column('last_test_date', sa.DateTime(), nullable=True))
    op.add_column('agent_metrics', sa.Column('test_history', postgresql.JSON(astext_type=sa.Text()), nullable=True))

def downgrade():
    op.drop_column('agent_metrics', 'test_history')
    op.drop_column('agent_metrics', 'last_test_date')
    op.drop_column('agent_metrics', 'consecutive_failures')
    op.drop_column('agent_metrics', 'consecutive_successes')
    op.drop_column('agent_metrics', 'total_tests_failed')
    op.drop_column('agent_metrics', 'total_tests_passed')
    op.drop_column('agent_metrics', 'total_tests_given') 