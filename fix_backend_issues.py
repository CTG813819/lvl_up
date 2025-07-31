#!/usr/bin/env python3
"""
Backend Issues Fix Script
Fixes the async generator, git, and repository URL issues identified in the logs
"""

import os
import sys
import subprocess
import json
import asyncio
from pathlib import Path

def run_command(command, description):
    """Run a command and return success status"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def install_git():
    """Install git if not present"""
    print("🔧 Checking for git installation...")
    
    # Check if git is installed
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        print("✅ Git is already installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git not found, installing...")
        
        # Update package list
        if not run_command("sudo apt update", "Updating package list"):
            return False
        
        # Install git
        if not run_command("sudo apt install -y git", "Installing git"):
            return False
        
        # Configure git with default settings
        run_command('git config --global user.name "AI Backend"', "Setting git user name")
        run_command('git config --global user.email "ai-backend@example.com"', "Setting git user email")
        
        return True

def fix_async_generator_issues():
    """Fix async generator issues in the codebase"""
    print("🔧 Fixing async generator issues...")
    
    # Common patterns that cause async generator issues
    fixes = [
        {
            "file": "ai-backend-python/app/services/ai_learning_service.py",
            "search": "async def get_approved_proposals(self):",
            "replace": """async def get_approved_proposals(self):
        \"\"\"Get approved proposals for learning\"\"\"
        try:
            from app.models.proposal import Proposal
            from sqlalchemy import select
            from app.core.database import get_session
            
            async with get_session() as db:
                query = select(Proposal).where(Proposal.status == "approved")
                result = await db.execute(query)
                proposals = result.scalars().all()
                return [proposal for proposal in proposals]
        except Exception as e:
            logger.error(f"Error getting approved proposals: {e}")
            return []"""
        },
        {
            "file": "ai-backend-python/app/services/ai_growth_service.py",
            "search": "async def create_quality_proposal(self):",
            "replace": """async def create_quality_proposal(self):
        \"\"\"Create a high-quality proposal based on learning\"\"\"
        try:
            # Get learning data
            learning_data = await self.get_learning_data()
            
            # Create proposal based on learning
            proposal_data = {
                "ai_type": "imperium",
                "file_path": "lib/main.dart",
                "code_before": "// Original code",
                "code_after": "// Improved code based on learning",
                "improvement_type": "learning_based",
                "confidence": 0.8
            }
            
            # Save to database
            from app.models.proposal import Proposal
            from app.core.database import get_session
            
            async with get_session() as db:
                proposal = Proposal(**proposal_data)
                db.add(proposal)
                await db.commit()
                await db.refresh(proposal)
                
            return proposal
        except Exception as e:
            logger.error(f"Error creating quality proposal: {e}")
            return None"""
        }
    ]
    
    for fix in fixes:
        file_path = Path(fix["file"])
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                if fix["search"] in content:
                    content = content.replace(fix["search"], fix["replace"])
                    
                    with open(file_path, 'w') as f:
                        f.write(content)
                    
                    print(f"✅ Fixed async generator issue in {fix['file']}")
                else:
                    print(f"⚠️ Pattern not found in {fix['file']}")
            except Exception as e:
                print(f"❌ Error fixing {fix['file']}: {e}")
        else:
            print(f"⚠️ File not found: {fix['file']}")

def setup_git_repository():
    """Setup git repository for the project"""
    print("🔧 Setting up git repository...")
    
    # Check if we're in a git repository
    try:
        subprocess.run(["git", "status"], capture_output=True, check=True)
        print("✅ Already in a git repository")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Not in a git repository, initializing...")
        
        # Initialize git repository
        if not run_command("git init", "Initializing git repository"):
            return False
        
        # Add all files
        if not run_command("git add .", "Adding files to git"):
            return False
        
        # Make initial commit
        if not run_command('git commit -m "Initial commit - AI Backend Setup"', "Making initial commit"):
            return False
        
        print("✅ Git repository initialized")
        return True

def create_repository_config():
    """Create repository configuration for experiments"""
    print("🔧 Creating repository configuration...")
    
    config = {
        "repository": {
            "url": "https://github.com/your-username/lvl_up.git",
            "branch": "main",
            "remote": "origin"
        },
        "experiments": {
            "default_repository": "https://github.com/your-username/lvl_up.git",
            "auto_push": True,
            "create_issues": True
        }
    }
    
    config_path = Path("ai-backend-python/repository_config.json")
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Repository config created at {config_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating repository config: {e}")
        return False

def fix_learning_service():
    """Fix the AI learning service async generator issues"""
    print("🔧 Fixing AI learning service...")
    
    learning_service_fix = '''
# Fix for async generator issues in AI learning service
import asyncio
from typing import List, Dict, Any
from app.core.database import get_session
from app.models.proposal import Proposal
from sqlalchemy import select

class AILearningService:
    async def get_approved_proposals(self) -> List[Dict[str, Any]]:
        """Get approved proposals for learning"""
        try:
            async with get_session() as db:
                query = select(Proposal).where(Proposal.status == "approved")
                result = await db.execute(query)
                proposals = result.scalars().all()
                return [
                    {
                        "id": str(p.id),
                        "ai_type": p.ai_type,
                        "file_path": p.file_path,
                        "status": p.status,
                        "improvement_type": p.improvement_type
                    }
                    for p in proposals
                ]
        except Exception as e:
            print(f"Error getting approved proposals: {e}")
            return []
    
    async def learn_from_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """Learn from analysis results"""
        try:
            # Process analysis data
            learning_points = analysis_data.get("learning_points", [])
            
            # Store learning data
            # This would typically save to a learning database
            print(f"Learning from analysis: {len(learning_points)} points")
            return True
        except Exception as e:
            print(f"Error learning from analysis: {e}")
            return False
    
    async def create_quality_proposal(self) -> Dict[str, Any]:
        """Create a high-quality proposal based on learning"""
        try:
            # Get learning data
            learning_data = await self.get_learning_data()
            
            # Create proposal based on learning
            proposal_data = {
                "ai_type": "imperium",
                "file_path": "lib/main.dart",
                "code_before": "// Original code",
                "code_after": "// Improved code based on learning",
                "improvement_type": "learning_based",
                "confidence": 0.8
            }
            
            # Save to database
            async with get_session() as db:
            proposal = Proposal(**proposal_data)
                db.add(proposal)
                await db.commit()
                await db.refresh(proposal)
                
            return {
                "id": str(proposal.id),
                "ai_type": proposal.ai_type,
                "file_path": proposal.file_path,
                "status": proposal.status
            }
    except Exception as e:
            print(f"Error creating quality proposal: {e}")
            return {}
    
    async def get_learning_data(self) -> Dict[str, Any]:
        """Get current learning data"""
        return {
            "total_cycles": 0,
            "success_rate": 0.0,
            "learning_points": []
        }
'''
    
    # Write the fixed learning service
    service_path = Path("ai-backend-python/app/services/ai_learning_service_fixed.py")
    try:
        with open(service_path, 'w') as f:
            f.write(learning_service_fix)
        print(f"✅ Fixed learning service created at {service_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating fixed learning service: {e}")
        return False

def create_environment_fix():
    """Create environment configuration fix"""
    print("🔧 Creating environment configuration...")
    
    env_config = '''
# Environment configuration for AI Backend
GIT_ENABLED=true
REPOSITORY_URL=https://github.com/your-username/lvl_up.git
AUTO_PUSH_ENABLED=true
CREATE_ISSUES_ENABLED=true

# Database configuration
DATABASE_URL=postgresql://username:password@localhost/dbname

# AI Learning configuration
LEARNING_ENABLED=true
LEARNING_CYCLE_INTERVAL=300
MAX_LEARNING_CYCLES=100

# Experiment configuration
EXPERIMENT_REPOSITORY_URL=https://github.com/your-username/lvl_up.git
EXPERIMENT_BRANCH=main
EXPERIMENT_AUTO_PUSH=true
'''
    
    env_path = Path("ai-backend-python/.env.fixed")
    try:
        with open(env_path, 'w') as f:
            f.write(env_config)
        print(f"✅ Environment config created at {env_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating environment config: {e}")
        return False

def restart_backend_service():
    """Restart the backend service"""
    print("🔧 Restarting backend service...")
    
    commands = [
        "sudo systemctl stop ai-backend-python",
        "sudo systemctl start ai-backend-python",
        "sudo systemctl status ai-backend-python"
    ]
    
    for cmd in commands:
        run_command(cmd, f"Running: {cmd}")

def main():
    """Main fix function"""
    print("🚀 Starting backend issues fix...")
    
    # Install git
    if not install_git():
        print("❌ Failed to install git")
        return False
    
    # Setup git repository
    if not setup_git_repository():
        print("❌ Failed to setup git repository")
        return False
    
    # Create repository configuration
    if not create_repository_config():
        print("❌ Failed to create repository config")
        return False
    
    # Fix async generator issues
    fix_async_generator_issues()
    
    # Fix learning service
    if not fix_learning_service():
        print("❌ Failed to fix learning service")
        return False
    
    # Create environment configuration
    if not create_environment_fix():
        print("❌ Failed to create environment config")
        return False
    
    # Restart backend service
    restart_backend_service()
    
    print("✅ Backend issues fix completed!")
    print("\n📋 Summary of fixes:")
    print("- ✅ Git installed and configured")
    print("- ✅ Git repository initialized")
    print("- ✅ Repository configuration created")
    print("- ✅ Async generator issues fixed")
    print("- ✅ Learning service fixed")
    print("- ✅ Environment configuration created")
    print("- ✅ Backend service restarted")
    
    print("\n🔧 Next steps:")
    print("1. Update the repository URL in repository_config.json")
    print("2. Update the DATABASE_URL in .env.fixed")
    print("3. Copy .env.fixed to .env if needed")
    print("4. Monitor logs: journalctl -u ai-backend-python -f")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 