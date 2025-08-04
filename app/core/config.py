"""
Configuration settings for the AI Backend
"""

import os
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, ConfigDict
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings"""
    
    # Database (using SQLite for local development, PostgreSQL for production)
    database_url: str = Field(default="sqlite:///./ai_backend.db", env="DATABASE_URL")
    database_name: str = Field(default="ai_backend", env="DATABASE_NAME")
    
    # Server
    port: int = Field(default=8000, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")
    debug: bool = Field(default=False, env="DEBUG")
    
    # AI Services
    # OpenAI removed to prevent authentication errors and timeouts
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4.1", env="OPENAI_MODEL")
    openai_max_tokens: int = Field(default=1024, env="OPENAI_MAX_TOKENS")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")

    # Anthropic
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-sonnet-20241022", env="ANTHROPIC_MODEL")
    anthropic_max_tokens: int = Field(default=1024, env="ANTHROPIC_MAX_TOKENS")

    # Token Usage Limits
    anthropic_monthly_limit: int = Field(default=40000, env="ANTHROPIC_MONTHLY_LIMIT")  # 40k tokens monthly
    openai_monthly_limit: int = Field(default=6000, env="OPENAI_MONTHLY_LIMIT")  # 6k tokens monthly
    enable_openai_fallback: bool = Field(default=True, env="ENABLE_OPENAI_FALLBACK")
    openai_fallback_threshold: float = Field(default=0.95, env="OPENAI_FALLBACK_THRESHOLD")  # Use OpenAI when Anthropic is 95% used
    
    google_api_key: Optional[str] = Field(default=None, env="GOOGLE_API_KEY")
    
    # GitHub
    github_token: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    github_repo: Optional[str] = Field(default=None, env="GITHUB_REPO")
    github_repo_url: Optional[str] = Field(default=None, env="GITHUB_REPO_URL")
    github_username: Optional[str] = Field(default=None, env="GITHUB_USERNAME")
    github_email: Optional[str] = Field(default=None, env="GITHUB_EMAIL")
    github_webhook_secret: Optional[str] = Field(default=None, env="GITHUB_WEBHOOK_SECRET")
    
    # AWS
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    aws_region: str = Field(default="us-east-1", env="AWS_REGION")
    
    # Twilio SMS Notifications
    twilio_account_sid: Optional[str] = Field(default=None, env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: Optional[str] = Field(default=None, env="TWILIO_AUTH_TOKEN")
    twilio_phone_number: Optional[str] = Field(default=None, env="TWILIO_PHONE_NUMBER")
    admin_phone_number: Optional[str] = Field(default=None, env="ADMIN_PHONE_NUMBER")
    
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
    
    # Flutter Validation
    skip_flutter_validation: bool = Field(default=False, env="SKIP_FLUTTER_VALIDATION")
    
    # Git Configuration (new fields that were causing errors)
    git_enabled: bool = Field(default=True, env="GIT_ENABLED")
    repository_url: Optional[str] = Field(default=None, env="REPOSITORY_URL")
    auto_push_enabled: bool = Field(default=True, env="AUTO_PUSH_ENABLED")
    create_issues_enabled: bool = Field(default=True, env="CREATE_ISSUES_ENABLED")
    
    # Learning Cycle Configuration
    learning_cycle_interval: int = Field(default=2100, env="LEARNING_CYCLE_INTERVAL")  # 35 minutes (between 30-45)
    max_learning_cycles: int = Field(default=100, env="MAX_LEARNING_CYCLES")
    
    # Experiment Configuration
    experiment_repository_url: Optional[str] = Field(default=None, env="EXPERIMENT_REPOSITORY_URL")
    experiment_branch: str = Field(default="main", env="EXPERIMENT_BRANCH")
    experiment_auto_push: bool = Field(default=True, env="EXPERIMENT_AUTO_PUSH")
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="allow"  # Allow extra fields from .env file
    )


# Create settings instance
settings = Settings() 