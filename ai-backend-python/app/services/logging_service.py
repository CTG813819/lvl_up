"""
Advanced Logging Service for AI Systems
Provides separate logging for different AI components with structured output
"""

import logging
import structlog
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum


class LogLevel(Enum):
    """Log levels for different AI systems"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AISystemType(Enum):
    """AI system types for separate logging"""
    PROJECT_HORUS = "project_horus"
    TRAINING_GROUND = "training_ground"
    ENHANCED_ADVERSARIAL = "enhanced_adversarial"
    CUSTODY_PROTOCOL = "custody_protocol"
    GENERAL = "general"


class AILoggingService:
    """Advanced logging service for AI systems"""
    
    def __init__(self):
        self.loggers = {}
        self._initialize_loggers()
    
    def _initialize_loggers(self):
        """Initialize separate loggers for each AI system"""
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
        
        # Create loggers for each AI system
        for system_type in AISystemType:
            logger = structlog.get_logger(system_type.value)
            self.loggers[system_type] = logger
    
    def log_project_horus(self, message: str, level: LogLevel = LogLevel.INFO, 
                         context: Optional[Dict[str, Any]] = None):
        """Log Project HORUS system events"""
        logger = self.loggers[AISystemType.PROJECT_HORUS]
        log_data = {
            "system": "project_horus",
            "message": message,
            "level": level.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        if level == LogLevel.DEBUG:
            logger.debug("", **log_data)
        elif level == LogLevel.INFO:
            logger.info("", **log_data)
        elif level == LogLevel.WARNING:
            logger.warning("", **log_data)
        elif level == LogLevel.ERROR:
            logger.error("", **log_data)
        elif level == LogLevel.CRITICAL:
            logger.critical("", **log_data)
    
    def log_training_ground(self, message: str, level: LogLevel = LogLevel.INFO,
                           context: Optional[Dict[str, Any]] = None):
        """Log Training Ground system events"""
        logger = self.loggers[AISystemType.TRAINING_GROUND]
        log_data = {
            "system": "training_ground",
            "message": message,
            "level": level.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        if level == LogLevel.DEBUG:
            logger.debug("", **log_data)
        elif level == LogLevel.INFO:
            logger.info("", **log_data)
        elif level == LogLevel.WARNING:
            logger.warning("", **log_data)
        elif level == LogLevel.ERROR:
            logger.error("", **log_data)
        elif level == LogLevel.CRITICAL:
            logger.critical("", **log_data)
    
    def log_enhanced_adversarial(self, message: str, level: LogLevel = LogLevel.INFO,
                                context: Optional[Dict[str, Any]] = None):
        """Log Enhanced Adversarial system events"""
        logger = self.loggers[AISystemType.ENHANCED_ADVERSARIAL]
        log_data = {
            "system": "enhanced_adversarial",
            "message": message,
            "level": level.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        if level == LogLevel.DEBUG:
            logger.debug("", **log_data)
        elif level == LogLevel.INFO:
            logger.info("", **log_data)
        elif level == LogLevel.WARNING:
            logger.warning("", **log_data)
        elif level == LogLevel.ERROR:
            logger.error("", **log_data)
        elif level == LogLevel.CRITICAL:
            logger.critical("", **log_data)
    
    def log_custody_protocol(self, message: str, level: LogLevel = LogLevel.INFO,
                            context: Optional[Dict[str, Any]] = None):
        """Log Custody Protocol system events"""
        logger = self.loggers[AISystemType.CUSTODY_PROTOCOL]
        log_data = {
            "system": "custody_protocol",
            "message": message,
            "level": level.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        if level == LogLevel.DEBUG:
            logger.debug("", **log_data)
        elif level == LogLevel.INFO:
            logger.info("", **log_data)
        elif level == LogLevel.WARNING:
            logger.warning("", **log_data)
        elif level == LogLevel.ERROR:
            logger.error("", **log_data)
        elif level == LogLevel.CRITICAL:
            logger.critical("", **log_data)
    
    def log_general(self, message: str, level: LogLevel = LogLevel.INFO,
                   context: Optional[Dict[str, Any]] = None):
        """Log general system events"""
        logger = self.loggers[AISystemType.GENERAL]
        log_data = {
            "system": "general",
            "message": message,
            "level": level.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        if level == LogLevel.DEBUG:
            logger.debug("", **log_data)
        elif level == LogLevel.INFO:
            logger.info("", **log_data)
        elif level == LogLevel.WARNING:
            logger.warning("", **log_data)
        elif level == LogLevel.ERROR:
            logger.error("", **log_data)
        elif level == LogLevel.CRITICAL:
            logger.critical("", **log_data)
    
    def log_test_execution(self, ai_type: str, test_type: str, score: float, 
                          passed: bool, duration: float, context: Optional[Dict[str, Any]] = None):
        """Log test execution results"""
        log_data = {
            "ai_type": ai_type,
            "test_type": test_type,
            "score": score,
            "passed": passed,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        message = f"Test execution completed for {ai_type} | Score: {score} | Passed: {passed} | Duration: {duration}s"
        
        if test_type == "custody_protocol":
            self.log_custody_protocol(message, LogLevel.INFO, log_data)
        elif test_type == "enhanced_adversarial":
            self.log_enhanced_adversarial(message, LogLevel.INFO, log_data)
        elif test_type == "training_ground":
            self.log_training_ground(message, LogLevel.INFO, log_data)
        else:
            self.log_general(message, LogLevel.INFO, log_data)
    
    def log_ai_evolution(self, ai_type: str, evolution_type: str, 
                        old_level: int, new_level: int, context: Optional[Dict[str, Any]] = None):
        """Log AI evolution events"""
        log_data = {
            "ai_type": ai_type,
            "evolution_type": evolution_type,
            "old_level": old_level,
            "new_level": new_level,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        message = f"AI evolution for {ai_type} | {evolution_type} | Level: {old_level} -> {new_level}"
        self.log_project_horus(message, LogLevel.INFO, log_data)
    
    def log_scenario_generation(self, system_type: AISystemType, scenario_type: str,
                              complexity: str, ai_types: list, context: Optional[Dict[str, Any]] = None):
        """Log scenario generation events"""
        log_data = {
            "scenario_type": scenario_type,
            "complexity": complexity,
            "ai_types": ai_types,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if context:
            log_data.update(context)
        
        message = f"Generated {scenario_type} scenario | Complexity: {complexity} | AIs: {ai_types}"
        
        if system_type == AISystemType.ENHANCED_ADVERSARIAL:
            self.log_enhanced_adversarial(message, LogLevel.INFO, log_data)
        elif system_type == AISystemType.TRAINING_GROUND:
            self.log_training_ground(message, LogLevel.INFO, log_data)
        else:
            self.log_general(message, LogLevel.INFO, log_data)


# Global instance
ai_logging_service = AILoggingService() 