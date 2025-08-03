#!/usr/bin/env python3
"""
Project Berserk Models
Models for Project Warmaster/Berserk functionality
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from typing import Optional


class ProjectBerserk(Base):
    """Project Berserk main model"""
    __tablename__ = "project_berserk"
    
    id = Column(Integer, primary_key=True, index=True)
    system_name = Column(String(255), default="HORUS")
    version = Column(String(50), default="1.0.0")
    status = Column(String(50), default="active")
    learning_progress = Column(Float, default=0.0)
    knowledge_base_size = Column(Integer, default=0)
    neural_connections = Column(Integer, default=0)
    capabilities = Column(JSON, default={})
    neural_network_structure = Column(JSON, default={})
    last_learning_session = Column(DateTime, nullable=True)
    last_self_improvement = Column(DateTime, nullable=True)
    is_learning = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class BerserkLearningSession(Base):
    """Berserk Learning Session model"""
    __tablename__ = "berserk_learning_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, index=True)
    topics = Column(JSON, default=[])
    session_type = Column(String(50), default="internet_learning")
    progress_gained = Column(Float, default=0.0)
    knowledge_increase = Column(Integer, default=0)
    neural_connections_added = Column(Integer, default=0)
    topics_learned = Column(JSON, default=[])
    duration_minutes = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())


class BerserkSelfImprovement(Base):
    """Berserk Self Improvement model"""
    __tablename__ = "berserk_self_improvements"
    
    id = Column(Integer, primary_key=True, index=True)
    improvement_id = Column(String(255), unique=True, index=True)
    improvement_type = Column(String(100))  # algorithm_optimization, model_generation, capability_enhancement
    performance_improvement = Column(Float, default=0.0)
    capability_enhancement = Column(Float, default=0.0)
    description = Column(Text)
    technical_details = Column(JSON, default={})
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=func.now())


class BerserkDeviceIntegration(Base):
    """Berserk Device Integration model"""
    __tablename__ = "berserk_device_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    device_name = Column(String(255))
    device_type = Column(String(100))
    device_id = Column(String(255), unique=True, index=True)
    connection_protocol = Column(String(100))
    capabilities = Column(JSON, default=[])
    status = Column(String(50), default="connected")
    user_id = Column(String(255), default="user_001")
    integration_level = Column(Float, default=0.0)
    last_activity = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 