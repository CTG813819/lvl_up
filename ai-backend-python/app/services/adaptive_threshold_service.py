"""
Adaptive Threshold Service
Manages dynamic passing thresholds for all testing systems
Thresholds adapt based on AI performance and test complexity
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import structlog
import json
import numpy as np
from sqlalchemy import select, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..models.sql_models import AgentMetrics
from .agent_metrics_service import AgentMetricsService

logger = structlog.get_logger()


class TestType(Enum):
    """Types of tests that have adaptive thresholds"""
    CUSTODES_STANDARD = "custodes_standard"
    OLYMPIC_TREATY = "olympic_treaty"
    COLLABORATIVE = "collaborative"
    ENHANCED_ADVERSARIAL = "enhanced_adversarial"


class TestComplexity(Enum):
    """Test complexity levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"
    LEGENDARY = "legendary"


class AdaptiveThresholdService:
    """Service for managing adaptive passing thresholds"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AdaptiveThresholdService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.agent_metrics_service = None
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the service"""
        instance = cls()
        instance.agent_metrics_service = AgentMetricsService()
        logger.info("Adaptive Threshold Service initialized")
        return instance
    
    def get_base_thresholds(self, test_type: TestType, complexity: TestComplexity) -> Tuple[int, int]:
        """Get base threshold range for a test type and complexity"""
        
        # Base thresholds by test type and complexity
        threshold_ranges = {
            TestType.CUSTODES_STANDARD: {
                TestComplexity.BASIC: (50, 70),
                TestComplexity.INTERMEDIATE: (55, 75),
                TestComplexity.ADVANCED: (60, 80),
                TestComplexity.EXPERT: (65, 85),
                TestComplexity.MASTER: (70, 90),
                TestComplexity.LEGENDARY: (75, 95)
            },
            TestType.OLYMPIC_TREATY: {
                TestComplexity.BASIC: (60, 80),
                TestComplexity.INTERMEDIATE: (65, 85),
                TestComplexity.ADVANCED: (70, 90),
                TestComplexity.EXPERT: (75, 95),
                TestComplexity.MASTER: (80, 100),
                TestComplexity.LEGENDARY: (85, 100)
            },
            TestType.COLLABORATIVE: {
                TestComplexity.BASIC: (50, 80),
                TestComplexity.INTERMEDIATE: (55, 85),
                TestComplexity.ADVANCED: (60, 90),
                TestComplexity.EXPERT: (65, 95),
                TestComplexity.MASTER: (70, 100),
                TestComplexity.LEGENDARY: (75, 100)
            },
            TestType.ENHANCED_ADVERSARIAL: {
                TestComplexity.BASIC: (50, 70),
                TestComplexity.INTERMEDIATE: (55, 75),
                TestComplexity.ADVANCED: (60, 80),
                TestComplexity.EXPERT: (65, 85),
                TestComplexity.MASTER: (70, 90),
                TestComplexity.LEGENDARY: (75, 95)
            }
        }
        
        return threshold_ranges[test_type][complexity]
    
    async def get_adaptive_threshold(self, test_type: TestType, complexity: TestComplexity, 
                                   ai_type: Optional[str] = None) -> int:
        """Get adaptive threshold based on recent AI performance"""
        
        base_min, base_max = self.get_base_thresholds(test_type, complexity)
        
        # Get recent performance data for all AIs
        all_metrics = await self.agent_metrics_service.get_all_agent_metrics()
        
        if not all_metrics:
            # If no data, return base threshold
            return base_min
        
        # Calculate recent performance trends
        recent_scores = []
        for ai, metrics in all_metrics.items():
            test_history = metrics.get("test_history", [])
            if test_history:
                # Get last 10 test scores
                recent_tests = test_history[-10:]
                for test in recent_tests:
                    if test.get("test_type") == test_type.value:
                        recent_scores.append(test.get("score", 0))
        
        if not recent_scores:
            return base_min
        
        # Calculate performance statistics
        avg_score = np.mean(recent_scores)
        std_score = np.std(recent_scores)
        
        # Adaptive threshold calculation
        if avg_score > base_max:
            # AIs are performing above max threshold - increase difficulty
            threshold_increase = min(10, (avg_score - base_max) * 0.5)
            adaptive_threshold = base_min + threshold_increase
        elif avg_score < base_min:
            # AIs are performing below min threshold - decrease difficulty
            threshold_decrease = min(5, (base_min - avg_score) * 0.3)
            adaptive_threshold = max(30, base_min - threshold_decrease)
        else:
            # AIs are performing within range - slight adjustment based on trend
            if len(recent_scores) >= 5:
                recent_trend = np.mean(recent_scores[-5:]) - np.mean(recent_scores[-10:-5])
                trend_adjustment = recent_trend * 0.2
                adaptive_threshold = base_min + trend_adjustment
            else:
                adaptive_threshold = base_min
        
        # Ensure threshold is within reasonable bounds
        adaptive_threshold = max(30, min(95, int(adaptive_threshold)))
        
        logger.info(f"Adaptive threshold for {test_type.value} {complexity.value}: "
                   f"base={base_min}, adaptive={adaptive_threshold}, "
                   f"avg_score={avg_score:.1f}, recent_tests={len(recent_scores)}")
        
        return adaptive_threshold
    
    async def get_ai_specific_threshold(self, test_type: TestType, complexity: TestComplexity, 
                                      ai_type: str) -> int:
        """Get AI-specific threshold based on individual performance"""
        
        # Get base adaptive threshold
        base_threshold = await self.get_adaptive_threshold(test_type, complexity)
        
        # Get AI-specific metrics
        ai_metrics = await self.agent_metrics_service.get_agent_metrics(ai_type)
        if not ai_metrics:
            return base_threshold
        
        test_history = ai_metrics.get("test_history", [])
        if not test_history:
            return base_threshold
        
        # Get AI's recent performance for this test type
        ai_recent_scores = []
        for test in test_history[-10:]:
            if test.get("test_type") == test_type.value:
                ai_recent_scores.append(test.get("score", 0))
        
        if not ai_recent_scores:
            return base_threshold
        
        ai_avg_score = np.mean(ai_recent_scores)
        ai_level = ai_metrics.get("level", 1)
        
        # Adjust threshold based on AI's individual performance
        if ai_avg_score > base_threshold + 10:
            # AI is performing well above threshold - increase difficulty
            ai_adjustment = min(15, (ai_avg_score - base_threshold) * 0.3)
            ai_threshold = base_threshold + ai_adjustment
        elif ai_avg_score < base_threshold - 10:
            # AI is struggling - decrease difficulty slightly
            ai_adjustment = min(10, (base_threshold - ai_avg_score) * 0.2)
            ai_threshold = max(30, base_threshold - ai_adjustment)
        else:
            # AI is performing around threshold - keep base
            ai_threshold = base_threshold
        
        # Level-based adjustment
        level_multiplier = 1 + (ai_level - 1) * 0.05  # 5% increase per level
        ai_threshold = int(ai_threshold * level_multiplier)
        
        # Ensure threshold is within bounds
        ai_threshold = max(30, min(95, ai_threshold))
        
        logger.info(f"AI-specific threshold for {ai_type} {test_type.value} {complexity.value}: "
                   f"base={base_threshold}, ai_specific={ai_threshold}, "
                   f"ai_avg={ai_avg_score:.1f}, level={ai_level}")
        
        return ai_threshold
    
    async def update_thresholds_after_test(self, test_type: TestType, complexity: TestComplexity,
                                         ai_type: str, score: int, passed: bool):
        """Update threshold calculations after a test is completed"""
        
        # This method can be used to fine-tune thresholds based on test results
        # For now, we'll just log the result for analysis
        logger.info(f"Test completed: {ai_type} {test_type.value} {complexity.value} "
                   f"score={score} passed={passed}")
        
        # Future: Implement more sophisticated threshold adjustment algorithms
        # based on test results, learning patterns, etc.
    
    async def get_threshold_analytics(self) -> Dict[str, Any]:
        """Get analytics about current threshold performance"""
        
        all_metrics = await self.agent_metrics_service.get_all_agent_metrics()
        
        analytics = {
            "test_types": {},
            "complexity_levels": {},
            "ai_performance": {},
            "threshold_effectiveness": {}
        }
        
        for test_type in TestType:
            analytics["test_types"][test_type.value] = {
                "total_tests": 0,
                "pass_rate": 0.0,
                "avg_score": 0.0,
                "current_thresholds": {}
            }
            
            for complexity in TestComplexity:
                base_min, base_max = self.get_base_thresholds(test_type, complexity)
                adaptive_threshold = await self.get_adaptive_threshold(test_type, complexity)
                
                analytics["test_types"][test_type.value]["current_thresholds"][complexity.value] = {
                    "base_min": base_min,
                    "base_max": base_max,
                    "adaptive_threshold": adaptive_threshold
                }
        
        # Calculate pass rates and average scores
        for ai_type, metrics in all_metrics.items():
            test_history = metrics.get("test_history", [])
            if test_history:
                ai_analytics = {
                    "total_tests": len(test_history),
                    "pass_rate": 0.0,
                    "avg_score": 0.0,
                    "recent_performance": []
                }
                
                scores = [test.get("score", 0) for test in test_history]
                passed_tests = [test for test in test_history if test.get("passed", False)]
                
                if scores:
                    ai_analytics["avg_score"] = np.mean(scores)
                if test_history:
                    ai_analytics["pass_rate"] = len(passed_tests) / len(test_history)
                
                # Recent performance (last 5 tests)
                recent_tests = test_history[-5:]
                ai_analytics["recent_performance"] = [
                    {"score": test.get("score", 0), "passed": test.get("passed", False)}
                    for test in recent_tests
                ]
                
                analytics["ai_performance"][ai_type] = ai_analytics
        
        return analytics 