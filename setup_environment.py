#!/usr/bin/env python3
"""
Environment Configuration Setup Script
Sets up the .env file with the provided configuration
"""

import os
import re
from pathlib import Path


def create_env_file():
    """Create or update the .env file with the provided configuration"""
    
    env_content = """# Environment configuration for AI Backend
GIT_ENABLED=true
REPOSITORY_URL=https://github.com/your-username/lvl_up.git
AUTO_PUSH_ENABLED=true
CREATE_ISSUES_ENABLED=true

# Database configuration
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_TV1hbOzC9ReA@ep-fragrant-night-aea4nuof-pooler.c-2.us-east-2.aws.neon.tech/neondb?ssl=require
DATABASE_NAME=neondb
PORT=4000
HOST=0.0.0.0
DEBUG=false

# AI Learning configuration
LEARNING_ENABLED=true
LEARNING_CYCLE_INTERVAL=300
MAX_LEARNING_CYCLES=100

# Experiment configuration
EXPERIMENT_REPOSITORY_URL=https://github.com/your-username/lvl_up.git
EXPERIMENT_BRANCH=main
EXPERIMENT_AUTO_PUSH=true

# AI Services Configuration
# OpenAI and Anthropic removed to prevent authentication errors and timeouts
GOOGLE_API_KEY=your_google_api_key_here

# GitHub Configuration
GITHUB_TOKEN=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
GITHUB_REPO=CTG813819/Lvl_UP
GITHUB_REPO_URL=https://github.com/CTG813819/Lvl_UP.git
GITHUB_USERNAME=CTG813819
GITHUB_EMAIL=canicegonzague@gmail.com
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1

# ML Settings
ML_MODEL_PATH=./models
ENABLE_ML_LEARNING=true
ML_CONFIDENCE_THRESHOLD=0.7

# NLP Settings
SPACY_MODEL=en_core_web_sm
NLTK_DATA_PATH=./nltk_data

# Security
CORS_ORIGINS=["*"]
TRUSTED_HOSTS=["*"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# File paths
UPLOAD_PATH=./uploads
TEMP_PATH=./temp

# AI Growth System
AUTO_IMPROVEMENT_ENABLED=true
GROWTH_ANALYSIS_INTERVAL=3600
GROWTH_THRESHOLD=0.6

# Repository Configuration
REPO_BRANCH=main
REPO_PATH=/home/ubuntu/ai-backend-python/repo

# Proposal settings
MAX_PROPOSAL_LENGTH=10000
PROPOSAL_TIMEOUT=300

# Flutter Validation
SKIP_FLUTTER_VALIDATION=false

# Learning Configuration
LEARNING_INTERVAL=300
MAX_LEARNING_HISTORY=1000
"""
    
    env_file = Path(".env")
    
    # Check if .env file exists
    if env_file.exists():
        print("⚠️  .env file already exists. Creating backup...")
        backup_file = Path(".env.backup")
        env_file.rename(backup_file)
        print(f"✅ Backup created: {backup_file}")
    
    # Write new .env file
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print("✅ Environment configuration file created successfully!")
    print(f"📁 File location: {env_file.absolute()}")
    
    return True


def validate_configuration():
    """Validate the configuration by checking required fields"""
    
    print("\n🔍 Validating configuration...")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found. Please run setup_environment.py first.")
        return False
    
    # Load and check key variables
    with open(".env", "r") as f:
        content = f.read()
    
    required_vars = [
        "DATABASE_URL",
        "GITHUB_TOKEN",
        "PORT",
        "HOST"
    ]
    
    missing_vars = []
    for var in required_vars:
        if f"{var}=" not in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing required environment variables: {', '.join(missing_vars)}")
        print("Please update the .env file with these values.")
        return False
    
    print("✅ Configuration validation passed!")
    return True


def update_github_config():
    """Interactive function to update GitHub configuration"""
    
    print("\n🔧 GitHub Configuration Setup")
    print("=" * 40)
    
    github_token = input("Enter your GitHub Personal Access Token: ").strip()
    github_username = input("Enter your GitHub username: ").strip()
    github_repo = input("Enter your repository name (username/repo): ").strip()
    
    if github_token and github_username and github_repo:
        # Update .env file
        with open(".env", "r") as f:
            content = f.read()
        
        # Replace GitHub configuration
        content = re.sub(r'GITHUB_TOKEN=.*', f'GITHUB_TOKEN={github_token}', content)
        content = re.sub(r'GITHUB_USERNAME=.*', f'GITHUB_USERNAME={github_username}', content)
        content = re.sub(r'GITHUB_REPO=.*', f'GITHUB_REPO={github_repo}', content)
        content = re.sub(r'GITHUB_REPO_URL=.*', f'GITHUB_REPO_URL=https://github.com/{github_repo}.git', content)
        content = re.sub(r'REPOSITORY_URL=.*', f'REPOSITORY_URL=https://github.com/{github_repo}.git', content)
        
        with open(".env", "w") as f:
            f.write(content)
        
        print("✅ GitHub configuration updated!")
        return True
    else:
        print("❌ Please provide all required GitHub information.")
        return False


def main():
    """Main setup function"""
    
    print("🚀 AI Backend Environment Configuration Setup")
    print("=" * 50)
    
    # Create .env file
    if create_env_file():
        print("\n✅ Environment file created successfully!")
        
        # Validate configuration
        if validate_configuration():
            print("\n🎉 Configuration setup completed!")
            print("\n📋 Next steps:")
            print("1. Update GitHub configuration (optional):")
            print("   python setup_environment.py --update-github")
            print("2. Start the backend:")
            print("   uvicorn app.main:app --host 0.0.0.0 --port 4000")
            print("3. Or use the systemd service:")
            print("   sudo systemctl restart ai-backend-python")
        else:
            print("\n⚠️  Please review and update the configuration as needed.")
    
    # Check for command line arguments
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--update-github":
        update_github_config()


if __name__ == "__main__":
    main() 