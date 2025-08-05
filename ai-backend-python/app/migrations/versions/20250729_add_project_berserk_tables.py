"""Add Project Berserk tables

Revision ID: 20250729_add_project_berserk_tables
Revises: 20250722_add_custody_metrics_to_agentmetrics
Create Date: 2025-07-29 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250729_add_project_berserk_tables'
down_revision = '20250722_add_custody_metrics_to_agentmetrics'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create project_berserk table
    op.create_table('project_berserk',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('system_name', sa.String(), nullable=True),
        sa.Column('version', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('learning_progress', sa.Float(), nullable=True),
        sa.Column('knowledge_base_size', sa.Integer(), nullable=True),
        sa.Column('neural_connections', sa.Integer(), nullable=True),
        sa.Column('self_generation_capability', sa.Float(), nullable=True),
        sa.Column('autonomous_decision_making', sa.Float(), nullable=True),
        sa.Column('nlp_capability', sa.Float(), nullable=True),
        sa.Column('voice_interaction', sa.Float(), nullable=True),
        sa.Column('device_control', sa.Float(), nullable=True),
        sa.Column('contextual_awareness', sa.Float(), nullable=True),
        sa.Column('personalization', sa.Float(), nullable=True),
        sa.Column('multimodal_interaction', sa.Float(), nullable=True),
        sa.Column('knowledge_domains', postgresql.JSON(), nullable=True),
        sa.Column('learned_skills', postgresql.JSON(), nullable=True),
        sa.Column('integrated_apis', postgresql.JSON(), nullable=True),
        sa.Column('device_integrations', postgresql.JSON(), nullable=True),
        sa.Column('generated_models', postgresql.JSON(), nullable=True),
        sa.Column('custom_algorithms', postgresql.JSON(), nullable=True),
        sa.Column('self_improvements', postgresql.JSON(), nullable=True),
        sa.Column('neural_network_structure', postgresql.JSON(), nullable=True),
        sa.Column('synapse_connections', postgresql.JSON(), nullable=True),
        sa.Column('learning_pathways', postgresql.JSON(), nullable=True),
        sa.Column('configuration', postgresql.JSON(), nullable=True),
        sa.Column('preferences', postgresql.JSON(), nullable=True),
        sa.Column('response_time_avg', sa.Float(), nullable=True),
        sa.Column('accuracy_rate', sa.Float(), nullable=True),
        sa.Column('uptime', sa.Float(), nullable=True),
        sa.Column('error_rate', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_learning_session', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_self_improvement', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create berserk_learning_sessions table
    op.create_table('berserk_learning_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('berserk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_type', sa.String(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('topics_learned', postgresql.JSON(), nullable=True),
        sa.Column('skills_acquired', postgresql.JSON(), nullable=True),
        sa.Column('progress_gained', sa.Float(), nullable=True),
        sa.Column('knowledge_increase', sa.Integer(), nullable=True),
        sa.Column('neural_connections_added', sa.Integer(), nullable=True),
        sa.Column('input_data', postgresql.JSON(), nullable=True),
        sa.Column('output_data', postgresql.JSON(), nullable=True),
        sa.Column('errors_encountered', postgresql.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['berserk_id'], ['project_berserk.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create berserk_self_improvements table
    op.create_table('berserk_self_improvements',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('berserk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('improvement_type', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('before_state', postgresql.JSON(), nullable=True),
        sa.Column('after_state', postgresql.JSON(), nullable=True),
        sa.Column('performance_improvement', sa.Float(), nullable=True),
        sa.Column('capability_enhancement', sa.Float(), nullable=True),
        sa.Column('efficiency_gain', sa.Float(), nullable=True),
        sa.Column('generated_code', sa.Text(), nullable=True),
        sa.Column('generated_model_path', sa.String(), nullable=True),
        sa.Column('configuration_changes', postgresql.JSON(), nullable=True),
        sa.Column('implemented_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['berserk_id'], ['project_berserk.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create berserk_device_integrations table
    op.create_table('berserk_device_integrations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('berserk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('device_name', sa.String(), nullable=True),
        sa.Column('device_type', sa.String(), nullable=True),
        sa.Column('device_id', sa.String(), nullable=True),
        sa.Column('connection_protocol', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('capabilities', postgresql.JSON(), nullable=True),
        sa.Column('control_commands', postgresql.JSON(), nullable=True),
        sa.Column('response_time', sa.Float(), nullable=True),
        sa.Column('reliability_score', sa.Float(), nullable=True),
        sa.Column('last_communication', sa.DateTime(timezone=True), nullable=True),
        sa.Column('configuration', postgresql.JSON(), nullable=True),
        sa.Column('security_settings', postgresql.JSON(), nullable=True),
        sa.Column('discovered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('connected_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['berserk_id'], ['project_berserk.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('berserk_device_integrations')
    op.drop_table('berserk_self_improvements')
    op.drop_table('berserk_learning_sessions')
    op.drop_table('project_berserk')