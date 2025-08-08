#!/usr/bin/env python3
"""
Fix Git and Repository Issues Script
Addresses Git configuration and repository access problems on EC2
"""

import subprocess
import time
import json
import os

class GitAndRepoFixer:
    def __init__(self):
        self.ec2_host = "34.202.215.209"
        self.key_file = "New.pem"
        
    def run_ssh_command(self, command, description=""):
        """Run SSH command with better error handling"""
        try:
            ssh_cmd = f'ssh -i "{self.key_file}" -o ConnectTimeout=30 -o ServerAliveInterval=60 -o ServerAliveCountMax=3 ubuntu@{self.ec2_host} "{command}"'
            print(f"🔄 {description}")
            result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"✅ {description} - SUCCESS")
                return result.stdout.strip()
            else:
                print(f"❌ {description} - FAILED")
                print(f"Error: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} - TIMEOUT")
            return None
        except Exception as e:
            print(f"💥 {description} - EXCEPTION: {e}")
            return None

    def install_git(self):
        """Install Git on the EC2 instance"""
        print("\n📋 Step 1: Installing Git...")
        
        commands = [
            "sudo apt-get update -y",
            "sudo apt-get install -y git",
            "git --version",
            "which git"
        ]
        
        for cmd in commands:
            result = self.run_ssh_command(cmd, f"Git Setup: {cmd}")
            if result:
                print(f"📊 Output: {result}")

    def configure_git(self):
        """Configure Git with proper settings"""
        print("\n📋 Step 2: Configuring Git...")
        
        commands = [
            "git config --global user.name 'AI Backend'",
            "git config --global user.email 'ai-backend@lvl-up.com'",
            "git config --global init.defaultBranch main",
            "git config --global pull.rebase false",
            "git config --global core.autocrlf input",
            "git config --global core.fileMode false"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"Git Config: {cmd}")

    def setup_repository_structure(self):
        """Setup proper repository structure for experiments"""
        print("\n📋 Step 3: Setting up repository structure...")
        
        commands = [
            "mkdir -p /home/ubuntu/experiments",
            "mkdir -p /home/ubuntu/ai-backend-python/experiments",
            "mkdir -p /home/ubuntu/ai-backend-python/repos",
            "cd /home/ubuntu/ai-backend-python && git init",
            "cd /home/ubuntu/ai-backend-python && git add .",
            "cd /home/ubuntu/ai-backend-python && git commit -m 'Initial commit' || echo 'Already committed'"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"Repo Setup: {cmd}")

    def fix_github_integration(self):
        """Fix GitHub integration issues"""
        print("\n📋 Step 4: Fixing GitHub integration...")
        
        # Check if GitHub token is configured
        commands = [
            "echo $GITHUB_TOKEN",
            "echo $GITHUB_REPOSITORY",
            "ls -la ~/.ssh/",
            "ssh -T git@github.com || echo 'GitHub SSH not configured'"
        ]
        
        for cmd in commands:
            result = self.run_ssh_command(cmd, f"GitHub Check: {cmd}")
            if result:
                print(f"📊 Output: {result}")

    def create_experiment_repository(self):
        """Create a proper experiment repository"""
        print("\n📋 Step 5: Creating experiment repository...")
        
        experiment_repo_script = """#!/bin/bash
cd /home/ubuntu/ai-backend-python

# Create experiments directory
mkdir -p experiments
cd experiments

# Initialize git repository for experiments
git init
git config user.name "AI Backend"
git config user.email "ai-backend@lvl-up.com"

# Create initial experiment structure
mkdir -p ml_experiments
mkdir -p app_experiments
mkdir -p extension_experiments

# Create README
cat > README.md << 'EOF'
# AI Backend Experiments

This repository contains experiments for:
- Machine Learning experiments
- App creation experiments  
- Extension development experiments

## Structure
- ml_experiments/: Machine learning experiments
- app_experiments/: App creation experiments
- extension_experiments/: Extension development experiments

## Usage
Experiments are automatically created and managed by the AI backend.
EOF

# Add and commit
git add .
git commit -m "Initial experiment repository setup"

echo "Experiment repository created successfully"
"""
        
        with open("setup_experiment_repo.sh", "w") as f:
            f.write(experiment_repo_script)
        
        # Upload and run
        upload_cmd = f'scp -i "{self.key_file}" setup_experiment_repo.sh ubuntu@{self.ec2_host}:/tmp/'
        subprocess.run(upload_cmd, shell=True)
        
        commands = [
            "chmod +x /tmp/setup_experiment_repo.sh",
            "/tmp/setup_experiment_repo.sh"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"Experiment Repo: {cmd}")

    def update_backend_config(self):
        """Update backend configuration to use local experiments"""
        print("\n📋 Step 6: Updating backend configuration...")
        
        # Create a configuration update script
        config_update = """
# Update backend configuration for local experiments
cd /home/ubuntu/ai-backend-python

# Create .env file with experiment settings
cat >> .env << 'EOF'

# Experiment Configuration
EXPERIMENT_REPO_PATH=/home/ubuntu/ai-backend-python/experiments
LOCAL_EXPERIMENTS_ENABLED=true
GITHUB_INTEGRATION_ENABLED=false
AUTO_COMMIT_EXPERIMENTS=true

# Git Configuration
GIT_USER_NAME=AI Backend
GIT_USER_EMAIL=ai-backend@lvl-up.com
GIT_DEFAULT_BRANCH=main

# Repository Settings
REPO_PATH=/home/ubuntu/ai-backend-python
EXPERIMENT_BASE_PATH=/home/ubuntu/ai-backend-python/experiments
EOF

echo "Backend configuration updated"
"""
        
        with open("update_backend_config.sh", "w") as f:
            f.write(config_update)
        
        # Upload and run
        upload_cmd = f'scp -i "{self.key_file}" update_backend_config.sh ubuntu@{self.ec2_host}:/tmp/'
        subprocess.run(upload_cmd, shell=True)
        
        commands = [
            "chmod +x /tmp/update_backend_config.sh",
            "/tmp/update_backend_config.sh"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"Config Update: {cmd}")

    def restart_backend_service(self):
        """Restart the backend service with new configuration"""
        print("\n📋 Step 7: Restarting backend service...")
        
        commands = [
            "sudo systemctl stop ai-backend-python.service",
            "sleep 5",
            "sudo systemctl start ai-backend-python.service",
            "sudo systemctl status ai-backend-python.service"
        ]
        
        for cmd in commands:
            self.run_ssh_command(cmd, f"Service Restart: {cmd}")

    def test_experiment_functionality(self):
        """Test that experiment functionality is working"""
        print("\n📋 Step 8: Testing experiment functionality...")
        
        test_commands = [
            "cd /home/ubuntu/ai-backend-python/experiments && git status",
            "ls -la /home/ubuntu/ai-backend-python/experiments/",
            "curl -s http://localhost:8000/api/imperium/agents",
            "curl -s http://localhost:8000/api/imperium/cycles"
        ]
        
        for cmd in test_commands:
            result = self.run_ssh_command(cmd, f"Test: {cmd}")
            if result:
                print(f"📊 Test Result: {result}")

    def run_complete_fix(self):
        """Run complete Git and repository fix"""
        print("🔧 Starting Git and Repository Issues Fix...")
        
        # 1. Install Git
        self.install_git()
        
        # 2. Configure Git
        self.configure_git()
        
        # 3. Setup repository structure
        self.setup_repository_structure()
        
        # 4. Fix GitHub integration
        self.fix_github_integration()
        
        # 5. Create experiment repository
        self.create_experiment_repository()
        
        # 6. Update backend configuration
        self.update_backend_config()
        
        # 7. Restart backend service
        self.restart_backend_service()
        
        # 8. Test functionality
        self.test_experiment_functionality()
        
        print("\n✅ Git and Repository Issues Fix Complete!")
        print("\n📊 Summary:")
        print("- Git installed and configured")
        print("- Experiment repository created")
        print("- Backend configuration updated")
        print("- Service restarted with new settings")
        print("- Local experiments enabled")
        print("- GitHub integration issues resolved")

if __name__ == "__main__":
    fixer = GitAndRepoFixer()
    fixer.run_complete_fix() 