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
    status = Column(String(20), default="pending", index=True)  # pending/accepted/rejected/tested
    user_feedback = Column(String(20), nullable=True)  # accepted/rejected
    test_status = Column(String(20), default="not-run")
    test_output = Column(Text, nullable=True)
    
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
Index('idx_guardian_suggestions_affected_item', GuardianSuggestion.affected_item_type, GuardianSuggestion.affected_item_id)
Index('idx_guardian_suggestions_severity', GuardianSuggestion.severity)
Index('idx_guardian_suggestions_created_at', GuardianSuggestion.created_at.desc())
Index('idx_guardian_suggestions_health_check_type', GuardianSuggestion.health_check_type) 