"""
Railway deployment utilities
Helps detect Railway environment and prevent startup issues
"""

import os
import structlog

logger = structlog.get_logger()

def is_railway_environment() -> bool:
    """
    Detect if running in Railway environment
    
    Returns:
        bool: True if running in Railway, False otherwise
    """
    # Railway provides these environment variables
    railway_indicators = [
        "PORT",                      # Railway always provides PORT
        "RAILWAY_ENVIRONMENT_NAME",  # Railway environment name  
        "RAILWAY_SERVICE_ID",        # Railway service ID
        "RAILWAY_PROJECT_ID",        # Railway project ID
        "RAILWAY_DEPLOYMENT_ID",     # Railway deployment ID
        "RAILWAY_PUBLIC_DOMAIN",     # Railway public domain
    ]
    
    for indicator in railway_indicators:
        if os.getenv(indicator):
            logger.info(f"Railway environment detected via {indicator}")
            return True
    
    return False

def should_skip_external_requests() -> bool:
    """
    Determine if external HTTP requests should be skipped
    
    This is useful for preventing startup hangs in containerized environments
    like Railway where external requests during initialization can cause issues.
    
    Returns:
        bool: True if external requests should be skipped
    """
    if is_railway_environment():
        logger.info("Skipping external requests due to Railway environment")
        return True
    
    # Could add other containerized environment detection here
    # e.g., Docker, Kubernetes, etc.
    
    return False

def get_environment_info() -> dict:
    """
    Get information about the current environment
    
    Returns:
        dict: Environment information
    """
    return {
        "is_railway": is_railway_environment(),
        "skip_external_requests": should_skip_external_requests(),
        "port": os.getenv("PORT"),
        "railway_service_id": os.getenv("RAILWAY_SERVICE_ID"),
        "railway_project_id": os.getenv("RAILWAY_PROJECT_ID"),
        "railway_environment": os.getenv("RAILWAY_ENVIRONMENT_NAME"),
    }