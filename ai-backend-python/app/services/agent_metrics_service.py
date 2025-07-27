"""
Agent Metrics Service - Single Source of Truth for All AI Agent Metrics
======================================================================

This service replaces all in-memory storage with direct database operations
using the NeonDB agent_metrics table as the single source of truth.

Key Features:
- Database-first approach (no in-memory caching)
- Real-time metrics updates
- Comprehensive metrics tracking
- Transaction safety
- Performance optimization with connection pooling
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_session
from app.models.sql_models import AgentMetrics
from app.core.config import settings

logger = structlog.get_logger()


class AgentMetricsService:
    """Centralized service for all agent metrics operations"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentMetricsService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the service"""
        instance = cls()
        logger.info("Agent Metrics Service initialized - using NeonDB as single source of truth")
        return instance
    
    # ==================== CORE METRICS OPERATIONS ====================
    
    async def get_agent_metrics(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific agent from database"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if agent_metrics:
                    return self._convert_to_dict(agent_metrics)
                return None
                
        except Exception as e:
            logger.error(f"Error getting metrics for {agent_type}", error=str(e))
            return None
    
    async def get_all_agent_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics for all agents from database"""
        try:
            async with get_session() as session:
                result = await session.execute(select(AgentMetrics))
                all_metrics = result.scalars().all()
                
                metrics_dict = {}
                for agent_metrics in all_metrics:
                    metrics_dict[agent_metrics.agent_type] = self._convert_to_dict(agent_metrics)
                
                return metrics_dict
                
        except Exception as e:
            logger.error("Error getting all agent metrics", error=str(e))
            return {}
    
    async def create_or_update_agent_metrics(self, agent_type: str, metrics_data: Dict[str, Any]) -> bool:
        """Create or update agent metrics in database"""
        try:
            async with get_session() as session:
                # Check if agent exists
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if agent_metrics:
                    # Update existing metrics
                    await self._update_metrics_fields(agent_metrics, metrics_data)
                else:
                    # Create new metrics
                    agent_metrics = AgentMetrics(
                        agent_id=f"{agent_type}_agent",
                        agent_type=agent_type,
                        **self._prepare_metrics_data(metrics_data)
                    )
                    session.add(agent_metrics)
                
                await session.commit()
                logger.info(f"Successfully updated metrics for {agent_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating metrics for {agent_type}", error=str(e))
            return False
    
    async def update_specific_metrics(self, agent_type: str, updates: Dict[str, Any]) -> bool:
        """Update specific metrics fields for an agent"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if agent_metrics:
                    await self._update_metrics_fields(agent_metrics, updates)
                    await session.commit()
                    logger.info(f"Updated specific metrics for {agent_type}")
                    return True
                else:
                    logger.warning(f"No metrics found for {agent_type}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating specific metrics for {agent_type}", error=str(e))
            return False
    
    # ==================== CUSTODY PROTOCOL METRICS ====================
    
    async def update_custody_test_result(self, agent_type: str, test_result: Dict[str, Any]) -> bool:
        """Update custody test results for an agent"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if not agent_metrics:
                    # Create new agent metrics if doesn't exist
                    agent_metrics = AgentMetrics(
                        agent_id=f"{agent_type}_agent",
                        agent_type=agent_type,
                        total_tests_given=0,
                        total_tests_passed=0,
                        total_tests_failed=0,
                        custody_level=1,
                        custody_xp=0,
                        consecutive_successes=0,
                        consecutive_failures=0,
                        test_history=[],
                        pass_rate=0.0,
                        failure_rate=0.0
                    )
                    session.add(agent_metrics)
                
                # Update test counts
                agent_metrics.total_tests_given += 1
                
                if test_result.get("passed", False):
                    agent_metrics.total_tests_passed += 1
                    agent_metrics.consecutive_successes += 1
                    agent_metrics.consecutive_failures = 0
                else:
                    agent_metrics.total_tests_failed += 1
                    agent_metrics.consecutive_failures += 1
                    agent_metrics.consecutive_successes = 0
                
                # Update pass/failure rates
                if agent_metrics.total_tests_given > 0:
                    agent_metrics.pass_rate = agent_metrics.total_tests_passed / agent_metrics.total_tests_given
                    agent_metrics.failure_rate = agent_metrics.total_tests_failed / agent_metrics.total_tests_given
                
                # Update test history
                test_history = list(agent_metrics.test_history or [])
                test_history.append({
                    "score": test_result.get("score", 0),
                    "passed": test_result.get("passed", False),
                    "duration": test_result.get("duration", 0),
                    "timestamp": test_result.get("timestamp", datetime.utcnow().isoformat())
                })
                agent_metrics.test_history = test_history[-50:]  # Keep last 50 tests
                
                # Update last test date
                agent_metrics.last_test_date = datetime.utcnow()
                
                # Award custody XP
                if test_result.get("passed", False):
                    xp_awarded = test_result.get("xp_awarded", 10)
                    agent_metrics.custody_xp += xp_awarded
                    
                    # Check for level up
                    new_level = await self._calculate_custody_level(agent_metrics.custody_xp)
                    if new_level > agent_metrics.custody_level:
                        agent_metrics.custody_level = new_level
                        logger.info(f"{agent_type} leveled up to custody level {new_level}")
                
                await session.commit()
                logger.info(f"Updated custody test results for {agent_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating custody test results for {agent_type}", error=str(e))
            return False
    
    async def get_custody_metrics(self, agent_type: str) -> Optional[Dict[str, Any]]:
        """Get custody-specific metrics for an agent"""
        try:
            metrics = await self.get_agent_metrics(agent_type)
            if metrics:
                return {
                    "total_tests_given": metrics.get("total_tests_given", 0),
                    "total_tests_passed": metrics.get("total_tests_passed", 0),
                    "total_tests_failed": metrics.get("total_tests_failed", 0),
                    "current_difficulty": metrics.get("current_difficulty", "basic"),
                    "last_test_date": metrics.get("last_test_date"),
                    "consecutive_failures": metrics.get("consecutive_failures", 0),
                    "consecutive_successes": metrics.get("consecutive_successes", 0),
                    "test_history": metrics.get("test_history", []),
                    "custody_level": metrics.get("custody_level", 1),
                    "custody_xp": metrics.get("custody_xp", 0),
                    "level": metrics.get("level", 1),
                    "xp": metrics.get("xp", 0),
                    "pass_rate": metrics.get("pass_rate", 0.0),
                    "failure_rate": metrics.get("failure_rate", 0.0)
                }
            return None
            
        except Exception as e:
            logger.error(f"Error getting custody metrics for {agent_type}", error=str(e))
            return None
    
    # ==================== LEARNING METRICS ====================
    
    async def update_learning_metrics(self, agent_type: str, learning_data: Dict[str, Any]) -> bool:
        """Update learning-related metrics for an agent"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if not agent_metrics:
                    # Create new agent metrics if doesn't exist
                    agent_metrics = AgentMetrics(
                        agent_id=f"{agent_type}_agent",
                        agent_type=agent_type,
                        learning_score=0.0,
                        success_rate=0.0,
                        failure_rate=0.0,
                        total_learning_cycles=0,
                        xp=0,
                        level=1,
                        prestige=0
                    )
                    session.add(agent_metrics)
                
                # Update learning score
                if "learning_score" in learning_data:
                    agent_metrics.learning_score = learning_data["learning_score"]
                
                # Update learning cycles
                if "learning_cycles" in learning_data:
                    agent_metrics.total_learning_cycles += learning_data["learning_cycles"]
                
                # Update XP and level
                if "xp_awarded" in learning_data:
                    agent_metrics.xp += learning_data["xp_awarded"]
                    new_level = await self._calculate_level(agent_metrics.xp)
                    if new_level > agent_metrics.level:
                        agent_metrics.level = new_level
                        logger.info(f"{agent_type} leveled up to level {new_level}")
                
                # Update success/failure rates
                if "success_rate" in learning_data:
                    agent_metrics.success_rate = learning_data["success_rate"]
                if "failure_rate" in learning_data:
                    agent_metrics.failure_rate = learning_data["failure_rate"]
                
                # Update learning patterns
                if "learning_patterns" in learning_data:
                    current_patterns = list(agent_metrics.learning_patterns or [])
                    current_patterns.extend(learning_data["learning_patterns"])
                    agent_metrics.learning_patterns = current_patterns[-100:]  # Keep last 100 patterns
                
                # Update improvement suggestions
                if "improvement_suggestions" in learning_data:
                    current_suggestions = list(agent_metrics.improvement_suggestions or [])
                    current_suggestions.extend(learning_data["improvement_suggestions"])
                    agent_metrics.improvement_suggestions = current_suggestions[-50:]  # Keep last 50 suggestions
                
                # Update timestamps
                agent_metrics.last_learning_cycle = datetime.utcnow()
                agent_metrics.updated_at = datetime.utcnow()
                
                await session.commit()
                logger.info(f"Updated learning metrics for {agent_type}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating learning metrics for {agent_type}", error=str(e))
            return False
    
    # ==================== UTILITY METHODS ====================
    
    def _convert_to_dict(self, agent_metrics: AgentMetrics) -> Dict[str, Any]:
        """Convert AgentMetrics object to dictionary"""
        return {
            "agent_id": agent_metrics.agent_id,
            "agent_type": agent_metrics.agent_type,
            "learning_score": agent_metrics.learning_score,
            "success_rate": agent_metrics.success_rate,
            "failure_rate": agent_metrics.failure_rate,
            "pass_rate": agent_metrics.pass_rate,
            "total_learning_cycles": agent_metrics.total_learning_cycles,
            "last_learning_cycle": agent_metrics.last_learning_cycle,
            "last_success": agent_metrics.last_success,
            "last_failure": agent_metrics.last_failure,
            "learning_patterns": list(agent_metrics.learning_patterns or []),
            "improvement_suggestions": list(agent_metrics.improvement_suggestions or []),
            "status": agent_metrics.status,
            "is_active": agent_metrics.is_active,
            "priority": agent_metrics.priority,
            "capabilities": agent_metrics.capabilities,
            "config": agent_metrics.config,
            "xp": agent_metrics.xp,
            "level": agent_metrics.level,
            "prestige": agent_metrics.prestige,
            "current_difficulty": agent_metrics.current_difficulty,
            "total_tests_given": agent_metrics.total_tests_given,
            "total_tests_passed": agent_metrics.total_tests_passed,
            "total_tests_failed": agent_metrics.total_tests_failed,
            "consecutive_successes": agent_metrics.consecutive_successes,
            "consecutive_failures": agent_metrics.consecutive_failures,
            "last_test_date": agent_metrics.last_test_date,
            "test_history": list(agent_metrics.test_history or []),
            "custody_level": agent_metrics.custody_level,
            "custody_xp": agent_metrics.custody_xp,
            "adversarial_wins": agent_metrics.adversarial_wins,
            "created_at": agent_metrics.created_at,
            "updated_at": agent_metrics.updated_at
        }
    
    def _prepare_metrics_data(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare metrics data for database insertion"""
        prepared_data = {}
        
        # Map common fields
        field_mapping = {
            "learning_score": "learning_score",
            "success_rate": "success_rate", 
            "failure_rate": "failure_rate",
            "pass_rate": "pass_rate",
            "total_learning_cycles": "total_learning_cycles",
            "xp": "xp",
            "level": "level",
            "prestige": "prestige",
            "current_difficulty": "current_difficulty",
            "total_tests_given": "total_tests_given",
            "total_tests_passed": "total_tests_passed",
            "total_tests_failed": "total_tests_failed",
            "consecutive_successes": "consecutive_successes",
            "consecutive_failures": "consecutive_failures",
            "custody_level": "custody_level",
            "custody_xp": "custody_xp",
            "adversarial_wins": "adversarial_wins",
            "learning_patterns": "learning_patterns",
            "improvement_suggestions": "improvement_suggestions",
            "test_history": "test_history",
            "capabilities": "capabilities",
            "config": "config",
            "status": "status",
            "is_active": "is_active",
            "priority": "priority"
        }
        
        for key, db_field in field_mapping.items():
            if key in metrics_data:
                prepared_data[db_field] = metrics_data[key]
        
        # Set defaults for required fields
        prepared_data.setdefault("learning_score", 0.0)
        prepared_data.setdefault("success_rate", 0.0)
        prepared_data.setdefault("failure_rate", 0.0)
        prepared_data.setdefault("pass_rate", 0.0)
        prepared_data.setdefault("total_learning_cycles", 0)
        prepared_data.setdefault("xp", 0)
        prepared_data.setdefault("level", 1)
        prepared_data.setdefault("prestige", 0)
        prepared_data.setdefault("current_difficulty", "basic")
        prepared_data.setdefault("total_tests_given", 0)
        prepared_data.setdefault("total_tests_passed", 0)
        prepared_data.setdefault("total_tests_failed", 0)
        prepared_data.setdefault("consecutive_successes", 0)
        prepared_data.setdefault("consecutive_failures", 0)
        prepared_data.setdefault("custody_level", 1)
        prepared_data.setdefault("custody_xp", 0)
        prepared_data.setdefault("adversarial_wins", 0)
        prepared_data.setdefault("learning_patterns", [])
        prepared_data.setdefault("improvement_suggestions", [])
        prepared_data.setdefault("test_history", [])
        prepared_data.setdefault("status", "idle")
        prepared_data.setdefault("is_active", True)
        prepared_data.setdefault("priority", "medium")
        
        return prepared_data
    
    async def _update_metrics_fields(self, agent_metrics: AgentMetrics, updates: Dict[str, Any]) -> None:
        """Update specific fields on an AgentMetrics object"""
        field_mapping = {
            "learning_score": "learning_score",
            "success_rate": "success_rate",
            "failure_rate": "failure_rate", 
            "pass_rate": "pass_rate",
            "total_learning_cycles": "total_learning_cycles",
            "xp": "xp",
            "level": "level",
            "prestige": "prestige",
            "current_difficulty": "current_difficulty",
            "total_tests_given": "total_tests_given",
            "total_tests_passed": "total_tests_passed",
            "total_tests_failed": "total_tests_failed",
            "consecutive_successes": "consecutive_successes",
            "consecutive_failures": "consecutive_failures",
            "custody_level": "custody_level",
            "custody_xp": "custody_xp",
            "adversarial_wins": "adversarial_wins",
            "learning_patterns": "learning_patterns",
            "improvement_suggestions": "improvement_suggestions",
            "test_history": "test_history",
            "capabilities": "capabilities",
            "config": "config",
            "status": "status",
            "is_active": "is_active",
            "priority": "priority"
        }
        
        for key, db_field in field_mapping.items():
            if key in updates:
                setattr(agent_metrics, db_field, updates[key])
        
        # Update timestamp
        agent_metrics.updated_at = datetime.utcnow()
    
    async def _calculate_level(self, xp: int) -> int:
        """Calculate level based on XP"""
        if xp < 1000:
            return 1
        elif xp < 5000:
            return 2
        elif xp < 10000:
            return 3
        elif xp < 25000:
            return 4
        elif xp < 50000:
            return 5
        elif xp < 100000:
            return 6
        elif xp < 250000:
            return 7
        elif xp < 500000:
            return 8
        elif xp < 1000000:
            return 9
        else:
            return 10
    
    async def _calculate_custody_level(self, custody_xp: int) -> int:
        """Calculate custody level based on custody XP"""
        if custody_xp < 100:
            return 1
        elif custody_xp < 300:
            return 2
        elif custody_xp < 600:
            return 3
        elif custody_xp < 1000:
            return 4
        elif custody_xp < 1500:
            return 5
        elif custody_xp < 2100:
            return 6
        elif custody_xp < 2800:
            return 7
        elif custody_xp < 3600:
            return 8
        elif custody_xp < 4500:
            return 9
        else:
            return 10
    
    async def update_custody_xp(self, agent_type: str, xp_amount: int) -> bool:
        """Update custody XP for an agent"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if agent_metrics:
                    # Update custody XP
                    agent_metrics.custody_xp = max(0, agent_metrics.custody_xp + xp_amount)
                    
                    # Recalculate custody level
                    agent_metrics.custody_level = await self._calculate_custody_level(agent_metrics.custody_xp)
                    
                    # Update timestamp
                    agent_metrics.updated_at = datetime.utcnow()
                    
                    await session.commit()
                    logger.info(f"Updated custody XP for {agent_type}: +{xp_amount} (Total: {agent_metrics.custody_xp}, Level: {agent_metrics.custody_level})")
                    return True
                else:
                    logger.warning(f"No metrics found for {agent_type}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error updating custody XP for {agent_type}", error=str(e))
            return False

    async def update_adversarial_test_result(self, agent_type: str, test_result: Dict[str, Any]) -> bool:
        """Update adversarial test results for an agent"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if not agent_metrics:
                    # Create new agent metrics if doesn't exist
                    agent_metrics = AgentMetrics(
                        agent_id=f"{agent_type}_agent",
                        agent_type=agent_type,
                        total_tests_given=0,
                        total_tests_passed=0,
                        total_tests_failed=0,
                        custody_level=1,
                        custody_xp=0,
                        consecutive_successes=0,
                        consecutive_failures=0,
                        test_history=[],
                        pass_rate=0.0,
                        failure_rate=0.0,
                        xp=0,
                        level=1,
                        adversarial_wins=0,
                        learning_score=0.0,
                        status="active"
                    )
                    session.add(agent_metrics)
                else:
                    # Ensure all fields are initialized to prevent None errors
                    if agent_metrics.total_tests_given is None:
                        agent_metrics.total_tests_given = 0
                    if agent_metrics.total_tests_passed is None:
                        agent_metrics.total_tests_passed = 0
                    if agent_metrics.total_tests_failed is None:
                        agent_metrics.total_tests_failed = 0
                    if agent_metrics.custody_xp is None:
                        agent_metrics.custody_xp = 0
                    if agent_metrics.consecutive_successes is None:
                        agent_metrics.consecutive_successes = 0
                    if agent_metrics.consecutive_failures is None:
                        agent_metrics.consecutive_failures = 0
                    if agent_metrics.xp is None:
                        agent_metrics.xp = 0
                    if agent_metrics.adversarial_wins is None:
                        agent_metrics.adversarial_wins = 0
                    if agent_metrics.test_history is None:
                        agent_metrics.test_history = []
                
                # Update test counts
                agent_metrics.total_tests_given += 1
                
                score = test_result.get("score", 0)
                passed = score >= 70
                
                if passed:
                    agent_metrics.total_tests_passed += 1
                    agent_metrics.consecutive_successes += 1
                    agent_metrics.consecutive_failures = 0
                else:
                    agent_metrics.total_tests_failed += 1
                    agent_metrics.consecutive_failures += 1
                    agent_metrics.consecutive_successes = 0
                
                # Update pass/failure rates
                if agent_metrics.total_tests_given > 0:
                    agent_metrics.pass_rate = agent_metrics.total_tests_passed / agent_metrics.total_tests_given
                    agent_metrics.failure_rate = agent_metrics.total_tests_failed / agent_metrics.total_tests_given
                
                # Update adversarial wins
                if test_result.get("is_winner", False):
                    agent_metrics.adversarial_wins += 1
                
                # Award XP
                xp_awarded = test_result.get("xp_awarded", 0)
                agent_metrics.xp += xp_awarded
                
                # Check for level up
                new_level = await self._calculate_level(agent_metrics.xp)
                if new_level > agent_metrics.level:
                    agent_metrics.level = new_level
                    logger.info(f"{agent_type} leveled up to level {new_level}")
                
                # Update test history
                test_history = list(agent_metrics.test_history or [])
                test_history.append({
                    "test_type": "adversarial",
                    "score": score,
                    "passed": passed,
                    "xp_awarded": xp_awarded,
                    "is_winner": test_result.get("is_winner", False),
                    "scenario_domain": test_result.get("scenario_domain", ""),
                    "scenario_complexity": test_result.get("scenario_complexity", ""),
                    "timestamp": test_result.get("timestamp", datetime.utcnow().isoformat()),
                    "winner_reasoning": test_result.get("winner_reasoning", None)
                })
                agent_metrics.test_history = test_history[-50:]  # Keep last 50 tests
                
                # Update last test date
                agent_metrics.last_test_date = datetime.utcnow()
                
                await session.commit()
                logger.info(f"Updated adversarial test results for {agent_type}: Score={score}, XP=+{xp_awarded}, Winner={test_result.get('is_winner', False)}")
                return True
                
        except Exception as e:
            logger.error(f"Error updating adversarial test results for {agent_type}", error=str(e))
            return False
    
    # ==================== BULK OPERATIONS ====================
    
    async def bulk_update_metrics(self, updates: Dict[str, Dict[str, Any]]) -> bool:
        """Bulk update metrics for multiple agents"""
        try:
            async with get_session() as session:
                for agent_type, metrics_data in updates.items():
                    result = await session.execute(
                        select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                    )
                    agent_metrics = result.scalar_one_or_none()
                    
                    if agent_metrics:
                        await self._update_metrics_fields(agent_metrics, metrics_data)
                    else:
                        # Create new agent metrics
                        agent_metrics = AgentMetrics(
                            agent_id=f"{agent_type}_agent",
                            agent_type=agent_type,
                            **self._prepare_metrics_data(metrics_data)
                        )
                        session.add(agent_metrics)
                
                await session.commit()
                logger.info(f"Bulk updated metrics for {len(updates)} agents")
                return True
                
        except Exception as e:
            logger.error("Error in bulk metrics update", error=str(e))
            return False
    
    async def reset_agent_metrics(self, agent_type: str) -> bool:
        """Reset all metrics for an agent"""
        try:
            async with get_session() as session:
                result = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == agent_type)
                )
                agent_metrics = result.scalar_one_or_none()
                
                if agent_metrics:
                    # Reset to default values
                    agent_metrics.learning_score = 0.0
                    agent_metrics.success_rate = 0.0
                    agent_metrics.failure_rate = 0.0
                    agent_metrics.pass_rate = 0.0
                    agent_metrics.total_learning_cycles = 0
                    agent_metrics.xp = 0
                    agent_metrics.level = 1
                    agent_metrics.prestige = 0
                    agent_metrics.current_difficulty = "basic"
                    agent_metrics.total_tests_given = 0
                    agent_metrics.total_tests_passed = 0
                    agent_metrics.total_tests_failed = 0
                    agent_metrics.consecutive_successes = 0
                    agent_metrics.consecutive_failures = 0
                    agent_metrics.custody_level = 1
                    agent_metrics.custody_xp = 0
                    agent_metrics.adversarial_wins = 0
                    agent_metrics.learning_patterns = []
                    agent_metrics.improvement_suggestions = []
                    agent_metrics.test_history = []
                    agent_metrics.status = "idle"
                    agent_metrics.is_active = True
                    agent_metrics.priority = "medium"
                    agent_metrics.updated_at = datetime.utcnow()
                    
                    await session.commit()
                    logger.info(f"Reset metrics for {agent_type}")
                    return True
                else:
                    logger.warning(f"No metrics found for {agent_type}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error resetting metrics for {agent_type}", error=str(e))
            return False 