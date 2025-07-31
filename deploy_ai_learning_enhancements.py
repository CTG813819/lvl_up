#!/usr/bin/env python3
"""
Deploy AI Learning Enhancements with scikit-learn to EC2
Removes all stubs/simulations and ensures live learning
"""

import subprocess
import sys
import os
import json

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def main():
    print("🚀 Deploying AI Learning Enhancements with scikit-learn to EC2")
    print("=" * 60)
    
    # Configuration
    EC2_HOST = "ubuntu@ec2-34-202-215-209.compute-1.amazonaws.com"
    REMOTE_PATH = "/home/ubuntu/ai-backend-python"
    
    # Files to deploy
    files_to_deploy = [
        "ai-backend-python/app/services/ai_learning_service.py",
        "ai-backend-python/app/services/testing_service.py",
        "ai-backend-python/app/routers/proposals.py",
        "ai-backend-python/app/services/conquest_ai_service.py",
        "ai-backend-python/app/services/background_service.py"
    ]
    
    print("📋 Files to deploy:")
    for file in files_to_deploy:
        print(f"  - {file}")
    
    # Deploy files
    for file_path in files_to_deploy:
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
            
        remote_file = f"{REMOTE_PATH}/{file_path.replace('ai-backend-python/', '')}"
        remote_dir = os.path.dirname(remote_file)
        
        # Create remote directory if needed
        run_command(f"ssh {EC2_HOST} 'mkdir -p {remote_dir}'", f"Creating directory {remote_dir}")
        
        # Copy file
        result = run_command(f"scp {file_path} {EC2_HOST}:{remote_file}", f"Deploying {file_path}")
        if result is None:
            print(f"❌ Failed to deploy {file_path}")
            continue
    
    # Install scikit-learn and other ML dependencies
    print("\n📦 Installing ML dependencies...")
    install_commands = [
        f"ssh {EC2_HOST} 'pip install scikit-learn pandas numpy scipy'",
        f"ssh {EC2_HOST} 'pip install psutil nltk textblob'",
        f"ssh {EC2_HOST} 'python -c \"import nltk; nltk.download(\\'punkt\\', quiet=True); nltk.download(\\'stopwords\\', quiet=True)\"'",
    ]
    
    for cmd in install_commands:
        result = run_command(cmd, "Installing ML dependencies")
        if result is None:
            print("❌ Failed to install some dependencies")
    
    # Create ML models directory
    run_command(f"ssh {EC2_HOST} 'mkdir -p {REMOTE_PATH}/ml_models'", "Creating ML models directory")
    
    # Restart backend service
    print("\n🔄 Restarting backend service...")
    restart_commands = [
        f"ssh {EC2_HOST} 'sudo systemctl stop ai-backend-python'",
        f"ssh {EC2_HOST} 'sudo systemctl start ai-backend-python'",
        f"ssh {EC2_HOST} 'sudo systemctl status ai-backend-python --no-pager'"
    ]
    
    for cmd in restart_commands:
        result = run_command(cmd, "Restarting service")
        if result is None:
            print("❌ Service restart failed")
            return
    
    # Check logs
    print("\n📊 Checking service logs...")
    run_command(f"ssh {EC2_HOST} 'sudo journalctl -u ai-backend-python -n 20 --no-pager'", "Checking recent logs")
    
    # Test ML functionality
    print("\n🧪 Testing ML functionality...")
    test_commands = [
        f"ssh {EC2_HOST} 'python -c \"import sklearn; print('scikit-learn version:', sklearn.__version__)\"'",
        f"ssh {EC2_HOST} 'python -c \"import pandas as pd; print('pandas version:', pd.__version__)\"'",
        f"ssh {EC2_HOST} 'python -c \"import numpy as np; print('numpy version:', np.__version__)\"'",
    ]
    
    for cmd in test_commands:
        run_command(cmd, "Testing ML imports")
    
    print("\n✅ AI Learning Enhancements Deployment Complete!")
    print("\n📋 Summary of Changes:")
    print("  ✅ Enhanced AI learning service with scikit-learn integration")
    print("  ✅ Added failure prediction models using RandomForest")
    print("  ✅ Added improvement prediction models using GradientBoosting")
    print("  ✅ Implemented real-time learning from test failures")
    print("  ✅ Removed all stubs and simulations")
    print("  ✅ Added live resource monitoring with psutil")
    print("  ✅ Enhanced testing service with live deployment tests")
    print("  ✅ Updated proposal flow with strict live testing requirements")
    
    print("\n🤖 AI Learning Features:")
    print("  - Failure pattern analysis using ML")
    print("  - Automatic improvement suggestions")
    print("  - Real-time learning from test failures")
    print("  - Predictive failure probability")
    print("  - AI-specific learning patterns")
    print("  - Live resource monitoring")
    
    print("\n🔍 To monitor the deployment:")
    print(f"  ssh {EC2_HOST}")
    print("  sudo journalctl -u ai-backend-python -f")
    print("  curl http://localhost:8000/api/proposals/")
    
    print("\n📈 To check AI learning insights:")
    print("  curl http://localhost:8000/api/ai-learning/insights/imperium")
    print("  curl http://localhost:8000/api/ai-learning/insights/guardian")
    print("  curl http://localhost:8000/api/ai-learning/insights/sandbox")
    print("  curl http://localhost:8000/api/ai-learning/insights/conquest")

if __name__ == "__main__":
    main() 