"""
Add explainability models for AI answers and learning records

Revision ID: 20250723_add_explainability_models
Revises: 20250723_add_custody_fields_to_agentmetrics
Create Date: 2025-07-23
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250723_add_explainability_models'
down_revision = '20250723_add_custody_fields_to_agentmetrics'
branch_labels = None
depends_on = None

def upgrade():
    # Create ai_answers table
    op.create_table('ai_answers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ai_type', sa.String(length=50), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=False),
        sa.Column('reasoning_trace', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, default=50.0),
        sa.Column('reasoning_quality', sa.String(length=20), nullable=True),
        sa.Column('uncertainty_areas', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('knowledge_applied', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('is_fallback', sa.Boolean(), nullable=True, default=False),
        sa.Column('self_assessment', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('learning_context_used', sa.Boolean(), nullable=True, default=False),
        sa.Column('learning_log', sa.Text(), nullable=True),
        sa.Column('prompt_length', sa.Integer(), nullable=True, default=0),
        sa.Column('answer_length', sa.Integer(), nullable=True, default=0),
        sa.Column('source', sa.String(length=50), nullable=True, default='ai_answer'),
        sa.Column('test_id', sa.String(length=100), nullable=True),
        sa.Column('test_category', sa.String(length=50), nullable=True),
        sa.Column('test_difficulty', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_answers_ai_type'), 'ai_answers', ['ai_type'], unique=False)
    op.create_index(op.f('ix_ai_answers_created_at'), 'ai_answers', ['created_at'], unique=False)
    op.create_index(op.f('ix_ai_answers_test_id'), 'ai_answers', ['test_id'], unique=False)

    # Create explainability_metrics table
    op.create_table('explainability_metrics',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ai_type', sa.String(length=50), nullable=False),
        sa.Column('average_confidence', sa.Float(), nullable=True, default=0.0),
        sa.Column('confidence_scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_trend', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('reasoning_quality_counts', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('uncertainty_patterns', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('top_uncertainty_areas', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_answers_logged', sa.Integer(), nullable=True, default=0),
        sa.Column('answers_with_uncertainty', sa.Integer(), nullable=True, default=0),
        sa.Column('answers_with_high_confidence', sa.Integer(), nullable=True, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_explainability_metrics_ai_type'), 'explainability_metrics', ['ai_type'], unique=False)
    op.create_index(op.f('ix_explainability_metrics_created_at'), 'explainability_metrics', ['created_at'], unique=False)

    # Create learning_records table
    op.create_table('learning_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ai_type', sa.String(length=50), nullable=False),
        sa.Column('learning_event', sa.String(length=100), nullable=False),
        sa.Column('learning_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=True, default=0.0),
        sa.Column('explainability_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, default=50.0),
        sa.Column('reasoning_quality', sa.String(length=20), nullable=True),
        sa.Column('has_uncertainty', sa.Boolean(), nullable=True, default=False),
        sa.Column('prompt_length', sa.Integer(), nullable=True, default=0),
        sa.Column('learning_context_used', sa.Boolean(), nullable=True, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_learning_records_ai_type'), 'learning_records', ['ai_type'], unique=False)
    op.create_index(op.f('ix_learning_records_learning_event'), 'learning_records', ['learning_event'], unique=False)
    op.create_index(op.f('ix_learning_records_created_at'), 'learning_records', ['created_at'], unique=False)

    # Create custody_test_results table
    op.create_table('custody_test_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('ai_type', sa.String(length=50), nullable=False),
        sa.Column('test_id', sa.String(length=100), nullable=False),
        sa.Column('test_category', sa.String(length=50), nullable=False),
        sa.Column('test_difficulty', sa.String(length=20), nullable=False),
        sa.Column('test_type', sa.String(length=50), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=True, default=False),
        sa.Column('score', sa.Float(), nullable=True, default=0.0),
        sa.Column('xp_awarded', sa.Integer(), nullable=True, default=0),
        sa.Column('learning_score_awarded', sa.Integer(), nullable=True, default=0),
        sa.Column('ai_responses', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('explainability_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('evaluation', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_custody_test_results_ai_type'), 'custody_test_results', ['ai_type'], unique=False)
    op.create_index(op.f('ix_custody_test_results_test_id'), 'custody_test_results', ['test_id'], unique=False)
    op.create_index(op.f('ix_custody_test_results_created_at'), 'custody_test_results', ['created_at'], unique=False)

def downgrade():
    op.drop_index(op.f('ix_custody_test_results_created_at'), table_name='custody_test_results')
    op.drop_index(op.f('ix_custody_test_results_test_id'), table_name='custody_test_results')
    op.drop_index(op.f('ix_custody_test_results_ai_type'), table_name='custody_test_results')
    op.drop_table('custody_test_results')
    
    op.drop_index(op.f('ix_learning_records_created_at'), table_name='learning_records')
    op.drop_index(op.f('ix_learning_records_learning_event'), table_name='learning_records')
    op.drop_index(op.f('ix_learning_records_ai_type'), table_name='learning_records')
    op.drop_table('learning_records')
    
    op.drop_index(op.f('ix_explainability_metrics_created_at'), table_name='explainability_metrics')
    op.drop_index(op.f('ix_explainability_metrics_ai_type'), table_name='explainability_metrics')
    op.drop_table('explainability_metrics')
    
    op.drop_index(op.f('ix_ai_answers_test_id'), table_name='ai_answers')
    op.drop_index(op.f('ix_ai_answers_created_at'), table_name='ai_answers')
    op.drop_index(op.f('ix_ai_answers_ai_type'), table_name='ai_answers')
    op.drop_table('ai_answers') 