"""
SQLAlchemy models for PostgreSQL/NeonDB
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.core.database import Base


class Proposal(Base):
    """Proposal model for PostgreSQL"""
    __tablename__ = "proposals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_type = Column(String(50), nullable=False, index=True)
    file_path = Column(String(500), nullable=False, index=True)
    code_before = Column(Text, nullable=False)
    code_after = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="pending", index=True)  # pending/accepted/rejected/tested
    user_feedback = Column(String(20), nullable=True)  # accepted/rejected
    test_status = Column(String(20), default="not-run")
    test_output = Column(Text, nullable=True)
    result = Column(Text, nullable=True)  # Store test results as JSON string
    
    # Advanced deduplication fields
    code_hash = Column(String(64), nullable=True, index=True)
    semantic_hash = Column(String(64), nullable=True, index=True)
    diff_score = Column(Float, nullable=True)
    duplicate_of = Column(UUID(as_uuid=True), ForeignKey("proposals.id"), nullable=True)
    
    # AI Learning fields
    ai_reasoning = Column(Text, nullable=True)
    learning_context = Column(Text, nullable=True)
    mistake_pattern = Column(String(200), nullable=True)
    improvement_type = Column(String(20), nullable=True)
    confidence = Column(Float, default=0.5)
    
    # Feedback and learning
    user_feedback_reason = Column(Text, nullable=True)
    ai_learning_applied = Column(Boolean, default=False)
    previous_mistakes_avoided = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    duplicates = relationship("Proposal", backref="original", remote_side=[id])


class Learning(Base):
    """Learning model for PostgreSQL"""
    __tablename__ = "learning"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_type = Column(String(50), nullable=False, index=True)
    learning_type = Column(String(50), nullable=False, index=True)
    pattern = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    confidence = Column(Float, default=0.5)
    applied_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ErrorLearning(Base):
    """Error learning model for PostgreSQL"""
    __tablename__ = "error_learning"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_type = Column(String(50), nullable=False, index=True)
    error_pattern = Column(String(200), nullable=False, index=True)
    error_message = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    solution = Column(Text, nullable=True)
    frequency = Column(Integer, default=1)
    last_occurred = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Experiment(Base):
    """Experiment model for PostgreSQL"""
    __tablename__ = "experiments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_type = Column(String(50), nullable=False, index=True)
    experiment_type = Column(String(50), nullable=False)
    parameters = Column(JSON, nullable=True)
    status = Column(String(20), default="running", index=True)
    results = Column(JSON, nullable=True)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)


class ExperimentRepository(Base):
    """Experiment repository model for PostgreSQL"""
    __tablename__ = "experiment_repositories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    agent_type = Column(String(50), nullable=False, index=True)  # Sandbox
    status = Column(String(20), default="active", index=True)  # active/inactive/archived
    repository_type = Column(String(50), default="github", index=True)  # github/local/gitlab
    is_private = Column(Boolean, default=True)
    
    # Repository statistics
    experiments_count = Column(Integer, default=0)
    total_commits = Column(Integer, default=0)
    last_activity = Column(DateTime, nullable=True)
    
    # Configuration
    auto_push_enabled = Column(Boolean, default=True)
    branch_name = Column(String(100), default="main")
    gitignore_template = Column(String(100), nullable=True)
    license_template = Column(String(100), nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # AI agent or user
    config = Column(JSON, nullable=True)  # Additional configuration
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AICapability(Base):
    """AI capability model for PostgreSQL"""
    __tablename__ = "ai_capabilities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_type = Column(String(50), nullable=False, unique=True)
    capabilities = Column(JSON, nullable=True)
    limitations = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AILearningHistory(Base):
    """AI learning history model for PostgreSQL"""
    __tablename__ = "ai_learning_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_type = Column(String(50), nullable=False, index=True)
    learning_event = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    impact_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# Create indexes for better performance
Index('idx_proposals_ai_type_status', Proposal.ai_type, Proposal.status)
Index('idx_proposals_file_path_ai_type', Proposal.file_path, Proposal.ai_type)
Index('idx_proposals_created_at', Proposal.created_at.desc())
Index('idx_proposals_code_hash_ai_type', Proposal.code_hash, Proposal.ai_type)
Index('idx_proposals_semantic_hash_ai_type', Proposal.semantic_hash, Proposal.ai_type)

Index('idx_learning_ai_type_created_at', Learning.ai_type, Learning.created_at.desc())
Index('idx_learning_learning_type', Learning.learning_type)

Index('idx_error_learning_ai_type_created_at', ErrorLearning.ai_type, ErrorLearning.created_at.desc())
Index('idx_error_learning_error_pattern', ErrorLearning.error_pattern)

Index('idx_experiments_ai_type_status', Experiment.ai_type, Experiment.status)
Index('idx_experiments_created_at', Experiment.created_at.desc())

Index('idx_experiment_repositories_agent_type', ExperimentRepository.agent_type)
Index('idx_experiment_repositories_status', ExperimentRepository.status)
Index('idx_experiment_repositories_created_at', ExperimentRepository.created_at.desc())


class ConquestDeployment(Base):
    """Conquest AI deployment model for PostgreSQL"""
    __tablename__ = "conquest_deployments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    app_name = Column(String(200), nullable=False, index=True)
    repository_url = Column(String(500), nullable=False)
    apk_url = Column(String(500), nullable=True)
    status = Column(String(20), default="pending", index=True)
    app_data = Column(JSON, nullable=True)
    build_logs = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create indexes for Conquest deployments
Index('idx_conquest_deployments_status', ConquestDeployment.status)
Index('idx_conquest_deployments_created_at', ConquestDeployment.created_at.desc())
Index('idx_conquest_deployments_app_name', ConquestDeployment.app_name)


class OathPaper(Base):
    """Oath Paper model for PostgreSQL"""
    __tablename__ = "oath_papers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False, index=True)
    content = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    ai_insights = Column(JSON, nullable=True)
    learning_value = Column(Float, default=0.0)
    status = Column(String(20), default="pending", index=True)  # pending/learned/failed
    ai_responses = Column(JSON, default=dict)  # {"Imperium": "learned", ...}
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Notification(Base):
    """Notification model for PostgreSQL"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), nullable=False, index=True)
    priority = Column(String(20), default="normal", index=True)
    read = Column(Boolean, default=False, index=True)
    notification_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Create indexes for new models
Index('idx_oath_papers_category', OathPaper.category)
Index('idx_oath_papers_created_at', OathPaper.created_at.desc())
Index('idx_oath_papers_status', OathPaper.status)
Index('idx_notifications_type_priority', Notification.type, Notification.priority)
Index('idx_notifications_read_created_at', Notification.read, Notification.created_at.desc())


class GuardianSuggestion(Base):
    """Guardian AI suggestion model for health checks and repairs"""
    __tablename__ = "guardian_suggestions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_type = Column(String(100), nullable=False, index=True)  # mission/entry/mastery
    affected_item_type = Column(String(50), nullable=False, index=True)  # mission/entry/mastery
    affected_item_id = Column(String(100), nullable=False, index=True)
    affected_item_name = Column(String(200), nullable=True)
    
    # Issue details
    issue_description = Column(Text, nullable=False)
    current_value = Column(Text, nullable=True)
    proposed_fix = Column(Text, nullable=False)
    severity = Column(String(20), default="medium", index=True)  # low/medium/high/critical
    
    # Health check metadata
    health_check_type = Column(String(100), nullable=False)  # id_validation/name_consistency/progress_check/etc
    logical_consistency = Column(Boolean, default=True)
    data_integrity_score = Column(Float, default=1.0)
    
    # User approval workflow
    status = Column(String(20), default="pending", index=True)  # pending/approved/rejected
    user_feedback = Column(Text, nullable=True)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Fix application tracking
    fix_applied = Column(Boolean, default=False)
    fix_applied_at = Column(DateTime, nullable=True)
    fix_result = Column(Text, nullable=True)
    fix_success = Column(Boolean, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata
    context_data = Column(JSON, nullable=True)  # Additional context about the issue
    related_items = Column(JSON, nullable=True)  # Related items that might be affected


# Create indexes for Guardian suggestions
Index('idx_guardian_suggestions_status', GuardianSuggestion.status)
Index('idx_guardian_suggestions_issue_type', GuardianSuggestion.issue_type)


class AgentMetrics(Base):
    """Agent metrics model for Imperium master orchestration"""
    __tablename__ = "agent_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), nullable=False, unique=True, index=True)
    agent_type = Column(String(50), nullable=False, index=True)
    learning_score = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    failure_rate = Column(Float, default=0.0)
    total_learning_cycles = Column(Integer, default=0)
    last_learning_cycle = Column(DateTime, nullable=True)
    last_success = Column(DateTime, nullable=True)
    last_failure = Column(DateTime, nullable=True)
    learning_patterns = Column(JSON, default=list)
    improvement_suggestions = Column(JSON, default=list)
    status = Column(String(20), default="idle", index=True)  # idle/learning/success/failed/paused
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(String(20), default="medium", index=True)
    capabilities = Column(JSON, nullable=True)
    config = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningCycle(Base):
    """Learning cycle model for Imperium master orchestration"""
    __tablename__ = "learning_cycles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cycle_id = Column(String(100), nullable=False, unique=True, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=True)
    participating_agents = Column(JSON, default=list)
    total_learning_value = Column(Float, default=0.0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    insights_generated = Column(JSON, default=list)
    status = Column(String(20), default="learning", index=True)  # learning/success/failed
    cycle_metadata = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class LearningLog(Base):
    """Learning log model for Imperium master orchestration"""
    __tablename__ = "learning_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100), nullable=False, index=True)  # internet_learning/agent_registration/cycle_complete/etc
    agent_id = Column(String(100), nullable=True, index=True)
    agent_type = Column(String(50), nullable=True, index=True)
    topic = Column(String(200), nullable=True)
    results_count = Column(Integer, default=0)
    results_sample = Column(JSON, nullable=True)  # Store sample of results
    insights = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    processing_time = Column(Float, nullable=True)
    impact_score = Column(Float, default=0.0)
    
    # Event data
    event_data = Column(JSON, nullable=True)  # Full event data
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class InternetLearningResult(Base):
    """Internet learning result model for Imperium master orchestration"""
    __tablename__ = "internet_learning_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), nullable=False, index=True)
    topic = Column(String(200), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)  # stackoverflow/github/arxiv/medium
    title = Column(String(500), nullable=True)
    url = Column(String(1000), nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    relevance_score = Column(Float, default=0.0)
    learning_value = Column(Float, default=0.0)
    insights_extracted = Column(JSON, nullable=True)
    applied_to_agent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# Create indexes for new Imperium models
Index('idx_agent_metrics_agent_id', AgentMetrics.agent_id)
Index('idx_agent_metrics_agent_type', AgentMetrics.agent_type)
Index('idx_agent_metrics_status', AgentMetrics.status)
Index('idx_agent_metrics_is_active', AgentMetrics.is_active)

Index('idx_learning_cycles_cycle_id', LearningCycle.cycle_id)
Index('idx_learning_cycles_start_time', LearningCycle.start_time.desc())
Index('idx_learning_cycles_status', LearningCycle.status)

Index('idx_learning_logs_event_type', LearningLog.event_type)
Index('idx_learning_logs_agent_id', LearningLog.agent_id)
Index('idx_learning_logs_created_at', LearningLog.created_at.desc())

Index('idx_internet_learning_results_agent_id', InternetLearningResult.agent_id)
Index('idx_internet_learning_results_topic', InternetLearningResult.topic)
Index('idx_internet_learning_results_source', InternetLearningResult.source)
Index('idx_internet_learning_results_created_at', InternetLearningResult.created_at.desc())
Index('idx_guardian_suggestions_affected_item', GuardianSuggestion.affected_item_type, GuardianSuggestion.affected_item_id)
Index('idx_guardian_suggestions_severity', GuardianSuggestion.severity)
Index('idx_guardian_suggestions_created_at', GuardianSuggestion.created_at.desc())
Index('idx_guardian_suggestions_health_check_type', GuardianSuggestion.health_check_type)


class Mission(Base):
    """Mission model for PostgreSQL"""
    __tablename__ = "missions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(String(100), nullable=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    mission_type = Column(String(50), nullable=False, index=True)
    is_completed = Column(Boolean, default=False, index=True)
    has_failed = Column(Boolean, default=False, index=True)
    mastery_id = Column(String(100), nullable=True, index=True)
    value = Column(Float, nullable=True)
    is_counter_based = Column(Boolean, default=False)
    current_count = Column(Integer, default=0)
    target_count = Column(Integer, default=0)
    mastery_value = Column(Float, default=0.0)
    linked_mastery_id = Column(String(100), nullable=True, index=True)
    notification_id = Column(Integer, nullable=False)
    scheduled_notification_id = Column(Integer, nullable=True)
    image_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    last_completed = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional metadata
    subtasks_data = Column(JSON, nullable=True)  # Store subtasks as JSON
    subtask_mastery_values = Column(JSON, nullable=True)  # Store mastery values as JSON
    bolt_color = Column(String(20), nullable=True)
    timelapse_color = Column(String(20), nullable=True)
    
    # Health check fields
    last_health_check = Column(DateTime, nullable=True)
    health_status = Column(String(20), default="unknown", index=True)
    data_integrity_score = Column(Float, default=1.0)


class MissionSubtask(Base):
    """Mission subtask model for PostgreSQL"""
    __tablename__ = "mission_subtasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mission_id = Column(UUID(as_uuid=True), ForeignKey("missions.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    required_completions = Column(Integer, default=0)
    current_completions = Column(Integer, default=0)
    linked_mastery_id = Column(String(100), nullable=True, index=True)
    mastery_value = Column(Float, default=0.0)
    is_counter_based = Column(Boolean, default=False)
    current_count = Column(Integer, default=0)
    bolt_color = Column(String(20), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mission = relationship("Mission", backref="subtasks")


# Create indexes for Mission models
Index('idx_missions_mission_id', Mission.mission_id)
Index('idx_missions_title', Mission.title)
Index('idx_missions_type', Mission.mission_type)
Index('idx_missions_completed', Mission.is_completed)
Index('idx_missions_health_status', Mission.health_status)
Index('idx_missions_created_at', Mission.created_at.desc())
Index('idx_mission_subtasks_mission_id', MissionSubtask.mission_id)
Index('idx_mission_subtasks_linked_mastery', MissionSubtask.linked_mastery_id) 