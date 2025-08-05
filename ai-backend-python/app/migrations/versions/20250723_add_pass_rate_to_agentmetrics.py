"""
Add pass_rate field to agent_metrics table

Revision ID: 20250723_add_pass_rate_to_agentmetrics
Revises: 20250722_add_custody_metrics_to_agentmetrics
Create Date: 2025-07-23
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250723_add_pass_rate_to_agentmetrics'
down_revision = '20250722_add_custody_metrics_to_agentmetrics'
branch_labels = None
depends_on = None

def upgrade():
    # Add pass_rate column to agent_metrics table
    op.add_column('agent_metrics', sa.Column('pass_rate', sa.Float(), nullable=True, server_default='0.0'))
    
    # Update existing records to calculate pass_rate from total_tests_passed and total_tests_given
    op.execute("""
        UPDATE agent_metrics 
        SET pass_rate = CASE 
            WHEN total_tests_given > 0 THEN CAST(total_tests_passed AS FLOAT) / CAST(total_tests_given AS FLOAT)
            ELSE 0.0 
        END
        WHERE pass_rate IS NULL
    """)

def downgrade():
    op.drop_column('agent_metrics', 'pass_rate') 