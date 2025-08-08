#!/usr/bin/env python3
"""
Simple script to install dependencies and set up backend environment
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Backend Dependencies...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("ai-backend-python"):
        print("❌ ai-backend-python directory not found. Please run this script from the project root.")
        sys.exit(1)
    
    # Change to ai-backend-python directory
    os.chdir("ai-backend-python")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        print("🔧 Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    
    # Activate virtual environment and install dependencies
    print("🔧 Installing Python dependencies...")
    
    # Install requirements
    install_cmd = "source venv/bin/activate && pip install -r requirements.txt"
    if not run_command(install_cmd, "Installing Python dependencies"):
        print("⚠️ Some dependencies may have failed to install. This is normal for system packages.")
    
    # Create basic .env file if it doesn't exist
    if not os.path.exists(".env"):
        print("🔧 Creating basic .env file...")
        env_content = """# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/ai_backend
DATABASE_NAME=ai_backend

# Server Configuration
PORT=4000
HOST=0.0.0.0
DEBUG=true

# AI Services (add your keys here)
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here

# GitHub Configuration (add your tokens here)
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=your_repo_name
GITHUB_REPO_URL=https://github.com/your_username/your_repo
GITHUB_USERNAME=your_github_username

# AWS Configuration (add your keys here)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# ML Settings
ML_MODEL_PATH=./models
ENABLE_ML_LEARNING=true
ML_CONFIDENCE_THRESHOLD=0.7

# Security
CORS_ORIGINS=["*"]
TRUSTED_HOSTS=["*"]

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# File paths
UPLOAD_PATH=./uploads
TEMP_PATH=./temp

# AI Learning
LEARNING_ENABLED=true
LEARNING_INTERVAL=300
MAX_LEARNING_HISTORY=1000

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
"""
        
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ Basic .env file created")
    
    # Create necessary directories
    directories = ["uploads", "temp", "models", "logs"]
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
    
    print("\n🎉 Backend setup completed!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Edit the .env file with your actual API keys and database URL")
    print("2. Set up your PostgreSQL database")
    print("3. Run the backend with: source venv/bin/activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 4000")
    print("\nNote: You'll need to configure your database URL in the .env file before the backend can fully start.")

if __name__ == "__main__":
    main() 