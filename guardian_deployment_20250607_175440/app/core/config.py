"""
Configuration settings for the AI Backend
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = Field(default="postgresql://user:password@localhost:5432/dbname", env="DATABASE_URL")
    database_name: str = Field(default="ai_backend", env="DATABASE_NAME")
    
    # Server
    port: int = Field(default=4000, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    debug: bool = Field(default=False, env="DEBUG")
    
    # AI Services
    # OpenAI removed to prevent authentication errors and timeouts
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    
    # GitHub
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    github_repo: Optional[str] = Field(default=None, env="GITHUB_REPO")
    github_repo_url: Optional[str] = Field(default=None, env="GITHUB_REPO_URL")
    github_username: Optional[str] = Field(default=None, env="GITHUB_USERNAME")
    github_webhook_secret: Optional[str] = Field(default=None, env="GITHUB_WEBHOOK_SECRET")
    
    # AWS
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    
    # ML Settings
    ml_model_path: str = Field(default="./models", env="ML_MODEL_PATH")
    enable_ml_learning: bool = Field(default=True, env="ENABLE_ML_LEARNING")
    ml_confidence_threshold: float = Field(default=0.7, env="ML_CONFIDENCE_THRESHOLD")
    
    # NLP Settings
    spacy_model: str = Field(default="en_core_web_sm", env="SPACY_MODEL")
    nltk_data_path: str = Field(default="./nltk_data", env="NLTK_DATA_PATH")
    
    # Security
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    trusted_hosts: List[str] = Field(default=["*"], env="TRUSTED_HOSTS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # File paths
    upload_path: str = Field(default="./uploads", env="UPLOAD_PATH")
    temp_path: str = Field(default="./temp", env="TEMP_PATH")
    
    # AI Learning
    learning_enabled: bool = Field(default=True, env="LEARNING_ENABLED")
    learning_interval: int = Field(default=300, env="LEARNING_INTERVAL")  # 5 minutes
    max_learning_history: int = Field(default=1000, env="MAX_LEARNING_HISTORY")
    
    # AI Growth System
    auto_improvement_enabled: bool = Field(default=True, env="AUTO_IMPROVEMENT_ENABLED")
    growth_analysis_interval: int = Field(default=3600, env="GROWTH_ANALYSIS_INTERVAL")
    growth_threshold: float = Field(default=0.6, env="GROWTH_THRESHOLD")
    
    # Repository Configuration
    repo_branch: str = Field(default="main", env="REPO_BRANCH")
    repo_path: str = Field(default="/home/ubuntu/ai-backend-python/repo", env="REPO_PATH")
    
    # Proposal settings
    max_proposal_length: int = Field(default=10000, env="MAX_PROPOSAL_LENGTH")
    proposal_timeout: int = Field(default=300, env="PROPOSAL_TIMEOUT")  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings() 