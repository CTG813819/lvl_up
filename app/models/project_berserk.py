from sqlalchemy import Column, String, DateTime, JSON, Float, Integer, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List


class ProjectBerserk(Base):
    """Model for Project Berserk - Autonomous JARVIS-like AI System"""
    __tablename__ = "project_berserk"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Core System Information
    system_name = Column(String, default="HORUS")  # HORUS - Hyper-Intelligent Omni-Responsive Universal System
    version = Column(String, default="1.0.0")
    status = Column(String, default="initializing")  # initializing, active, learning, evolving, error
    
    # Learning Progress (0-100, but never reaches 100 as internet grows)
    learning_progress = Column(Float, default=0.0)
    knowledge_base_size = Column(Integer, default=0)
    neural_connections = Column(Integer, default=0)
    self_generation_capability = Column(Float, default=0.0)
    autonomous_decision_making = Column(Float, default=0.0)
    
    # Capabilities Tracking
    nlp_capability = Column(Float, default=0.0)
    voice_interaction = Column(Float, default=0.0)
    device_control = Column(Float, default=0.0)
    contextual_awareness = Column(Float, default=0.0)
    personalization = Column(Float, default=0.0)
    multimodal_interaction = Column(Float, default=0.0)
    
    # Knowledge Base
    knowledge_domains = Column(JSON, default=list)  # List of domains it has learned
    learned_skills = Column(JSON, default=list)  # List of acquired skills
    integrated_apis = Column(JSON, default=list)  # List of integrated external services
    device_integrations = Column(JSON, default=list)  # List of controlled devices
    
    # Self-Generation Components
    generated_models = Column(JSON, default=list)  # List of self-generated ML models
    custom_algorithms = Column(JSON, default=list)  # List of custom algorithms created
    self_improvements = Column(JSON, default=list)  # List of self-improvements made
    
    # Brain Visualization Data
    neural_network_structure = Column(JSON, default=dict)  # Structure for brain visualization
    synapse_connections = Column(JSON, default=list)  # Synapse data for visualization
    learning_pathways = Column(JSON, default=list)  # Learning pathway visualization
    
    # System Configuration
    configuration = Column(JSON, default=dict)  # System configuration
    preferences = Column(JSON, default=dict)  # User preferences and settings
    
    # Performance Metrics
    response_time_avg = Column(Float, default=0.0)
    accuracy_rate = Column(Float, default=0.0)
    uptime = Column(Float, default=0.0)
    error_rate = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_learning_session = Column(DateTime(timezone=True))
    last_self_improvement = Column(DateTime(timezone=True))
    
    # Metadata
    description = Column(Text, default="Autonomous JARVIS-like AI system that learns, grows, and self-improves")
    notes = Column(Text)
    is_active = Column(Boolean, default=True)


class BerserkLearningSession(Base):
    """Model for tracking individual learning sessions"""
    __tablename__ = "berserk_learning_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    berserk_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Session Information
    session_type = Column(String)  # nlp, voice, device_control, etc.
    duration_minutes = Column(Integer, default=0)
    topics_learned = Column(JSON, default=list)
    skills_acquired = Column(JSON, default=list)
    
    # Progress Metrics
    progress_gained = Column(Float, default=0.0)
    knowledge_increase = Column(Integer, default=0)
    neural_connections_added = Column(Integer, default=0)
    
    # Session Data
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    errors_encountered = Column(JSON, default=list)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BerserkSelfImprovement(Base):
    """Model for tracking self-improvements made by the system"""
    __tablename__ = "berserk_self_improvements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    berserk_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Improvement Information
    improvement_type = Column(String)  # algorithm, model, capability, etc.
    description = Column(Text)
    before_state = Column(JSON, default=dict)
    after_state = Column(JSON, default=dict)
    
    # Impact Metrics
    performance_improvement = Column(Float, default=0.0)
    capability_enhancement = Column(Float, default=0.0)
    efficiency_gain = Column(Float, default=0.0)
    
    # Generated Code/Models
    generated_code = Column(Text)
    generated_model_path = Column(String)
    configuration_changes = Column(JSON, default=dict)
    
    # Timestamps
    implemented_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BerserkDeviceIntegration(Base):
    """Model for tracking device integrations"""
    __tablename__ = "berserk_device_integrations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    berserk_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Device Information
    device_name = Column(String)
    device_type = Column(String)  # iot, mobile, desktop, api, etc.
    device_id = Column(String)
    connection_protocol = Column(String)  # mqtt, http, bluetooth, etc.
    
    # Integration Status
    status = Column(String, default="discovered")  # discovered, connecting, connected, controlling, error
    capabilities = Column(JSON, default=list)
    control_commands = Column(JSON, default=list)
    
    # Performance Metrics
    response_time = Column(Float, default=0.0)
    reliability_score = Column(Float, default=0.0)
    last_communication = Column(DateTime(timezone=True))
    
    # Configuration
    configuration = Column(JSON, default=dict)
    security_settings = Column(JSON, default=dict)
    
    # Timestamps
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    connected_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())