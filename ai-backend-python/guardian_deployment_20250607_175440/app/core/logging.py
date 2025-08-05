"""
Logging configuration
"""

import sys
import structlog
from typing import Any, Dict
from .config import settings


def setup_logging():
    """Setup structured logging"""
    
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
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    import logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level.upper()),
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a logger instance"""
    return structlog.get_logger(name)


def log_function_call(func_name: str, **kwargs) -> Dict[str, Any]:
    """Log function call with parameters"""
    logger = get_logger()
    logger.info(
        "Function called",
        function=func_name,
        parameters=kwargs
    )
    return {"function": func_name, "parameters": kwargs}


def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Log error with context"""
    logger = get_logger()
    logger.error(
        "Error occurred",
        error_type=type(error).__name__,
        error_message=str(error),
        context=context or {}
    ) 