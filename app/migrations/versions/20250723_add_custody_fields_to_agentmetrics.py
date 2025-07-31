"""
Add custody_level and custody_xp fields to agent_metrics table

Revision ID: 20250723_add_custody_fields_to_agentmetrics
Revises: 20250723_add_pass_rate_to_agentmetrics
Create Date: 2025-07-23
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20250723_add_custody_fields_to_agentmetrics'
down_revision = '20250723_add_pass_rate_to_agentmetrics'
branch_labels = None
depends_on = None

def upgrade():
    # Add custody_level and custody_xp columns to agent_metrics table
    op.add_column('agent_metrics', sa.Column('custody_level', sa.Integer(), nullable=True, server_default='1'))
    op.add_column('agent_metrics', sa.Column('custody_xp', sa.Integer(), nullable=True, server_default='0'))
    
    # Update existing records to set custody_level = level and custody_xp = xp
    op.execute("""
        UPDATE agent_metrics 
        SET custody_level = level, custody_xp = xp 
        WHERE custody_level IS NULL OR custody_xp IS NULL
    """)

def downgrade():
    # Remove the added columns
    op.drop_column('agent_metrics', 'custody_xp')
    op.drop_column('agent_metrics', 'custody_level') 