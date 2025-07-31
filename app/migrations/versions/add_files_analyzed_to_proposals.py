"""
Add files_analyzed column to proposals table

Revision ID: add_files_analyzed_to_proposals
Revises: <previous_revision_id>
Create Date: 2024-07-14
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_files_analyzed_to_proposals'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('proposals', sa.Column('files_analyzed', sa.JSON(), nullable=True))

def downgrade():
    op.drop_column('proposals', 'files_analyzed') 