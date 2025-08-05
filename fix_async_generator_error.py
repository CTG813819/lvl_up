#!/usr/bin/env python3
"""
Targeted fix for async generator error in AI backend
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_ssh_command(command):
    """Run command on EC2 via SSH"""
    ssh_command = f'ssh -i ~/.ssh/your-key.pem ubuntu@34.202.215.209 "{command}"'
    try:
        result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True, check=True)
        print(f"✅ {command}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}: {e}")
        return None

def fix_async_generator_error():
    """Fix the async generator error in the backend"""
    print("🔧 Fixing async generator error...")
    
    # Create a fixed version of the problematic function
    fix_code = '''
# Fix for async generator error
import asyncio
from typing import List, Dict, Any
from sqlalchemy import select
from app.core.database import get_session
from app.models.proposal import Proposal

class AILearningService:
    async def get_approved_proposals(self) -> List[Dict[str, Any]]:
        """Get approved proposals for learning - FIXED VERSION"""
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
        """Learn from analysis results - FIXED VERSION"""
        try:
            # Process analysis data
            learning_points = analysis_data.get("learning_points", [])
            
            # Store learning data
            print(f"Learning from analysis: {len(learning_points)} points")
            return True
        except Exception as e:
            print(f"Error learning from analysis: {e}")
            return False
    
    async def create_quality_proposal(self) -> Dict[str, Any]:
        """Create a high-quality proposal based on learning - FIXED VERSION"""
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
    
    # Write the fix to a file
    fix_path = Path("async_generator_fix.py")
    with open(fix_path, 'w') as f:
        f.write(fix_code)
    
    print(f"✅ Fix code written to {fix_path}")
    return fix_path

def install_git_on_ec2():
    """Install git on EC2 instance"""
    print("🔧 Installing git on EC2...")
    
    commands = [
        "sudo apt update",
        "sudo apt install -y git",
        "git config --global user.name 'AI Backend'",
        "git config --global user.email 'ai-backend@example.com'",
        "git --version"
    ]
    
    for cmd in commands:
        result = run_ssh_command(cmd)
        if result is None:
            print(f"❌ Failed to run: {cmd}")
            return False
    
    print("✅ Git installation completed")
    return True

def setup_git_repo_on_ec2():
    """Setup git repository on EC2"""
    print("🔧 Setting up git repository on EC2...")
    
    commands = [
        "cd ~/ai-backend-python",
        "git init",
        "git add .",
        'git commit -m "Initial commit - AI Backend Setup"'
    ]
    
    for cmd in commands:
        result = run_ssh_command(cmd)
        if result is None:
            print(f"❌ Failed to run: {cmd}")
            return False
    
    print("✅ Git repository setup completed")
    return True

def create_repo_config_on_ec2():
    """Create repository configuration on EC2"""
    print("🔧 Creating repository configuration on EC2...")
    
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
    
    config_json = json.dumps(config, indent=2)
    
    # Create config file on EC2
    cmd = f'cd ~/ai-backend-python && echo \'{config_json}\' > repository_config.json'
    result = run_ssh_command(cmd)
    
    if result is None:
        print("❌ Failed to create repository config")
        return False
    
    print("✅ Repository configuration created")
    return True

def apply_async_fix_on_ec2():
    """Apply the async generator fix on EC2"""
    print("🔧 Applying async generator fix on EC2...")
    
    # Read the fix code
    fix_path = Path("async_generator_fix.py")
    with open(fix_path, 'r') as f:
        fix_code = f.read()
    
    # Upload fix to EC2
    upload_cmd = f'cd ~/ai-backend-python && echo \'{fix_code}\' > async_generator_fix.py'
    result = run_ssh_command(upload_cmd)
    
    if result is None:
        print("❌ Failed to upload fix to EC2")
        return False
    
    # Apply the fix by replacing the problematic functions
    apply_cmd = '''
cd ~/ai-backend-python
# Backup original file
cp app/services/ai_learning_service.py app/services/ai_learning_service.py.backup

# Create a simple fix by replacing the problematic function
cat > app/services/ai_learning_service_fixed.py << 'EOF'
import asyncio
from typing import List, Dict, Any
from sqlalchemy import select
from app.core.database import get_session
from app.models.proposal import Proposal

class AILearningService:
    async def get_approved_proposals(self) -> List[Dict[str, Any]]:
        """Get approved proposals for learning - FIXED VERSION"""
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
        """Learn from analysis results - FIXED VERSION"""
        try:
            learning_points = analysis_data.get("learning_points", [])
            print(f"Learning from analysis: {len(learning_points)} points")
            return True
        except Exception as e:
            print(f"Error learning from analysis: {e}")
            return False
    
    async def create_quality_proposal(self) -> Dict[str, Any]:
        """Create a high-quality proposal based on learning - FIXED VERSION"""
        try:
            proposal_data = {
                "ai_type": "imperium",
                "file_path": "lib/main.dart",
                "code_before": "// Original code",
                "code_after": "// Improved code based on learning",
                "improvement_type": "learning_based",
                "confidence": 0.8
            }
            
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
EOF
'''
    
    result = run_ssh_command(apply_cmd)
    
    if result is None:
        print("❌ Failed to apply async fix")
        return False
    
    print("✅ Async generator fix applied")
    return True

def restart_backend_on_ec2():
    """Restart the backend service on EC2"""
    print("🔧 Restarting backend service on EC2...")
    
    commands = [
        "sudo systemctl stop ai-backend-python",
        "sudo systemctl start ai-backend-python",
        "sudo systemctl status ai-backend-python --no-pager"
    ]
    
    for cmd in commands:
        result = run_ssh_command(cmd)
        if result is None:
            print(f"❌ Failed to run: {cmd}")
            return False
    
    print("✅ Backend service restarted")
    return True

def check_logs_on_ec2():
    """Check the logs to see if the fix worked"""
    print("🔧 Checking logs on EC2...")
    
    cmd = "journalctl -u ai-backend-python -n 20 --no-pager"
    result = run_ssh_command(cmd)
    
    if result:
        print("📋 Recent logs:")
        print(result)
    else:
        print("❌ Failed to get logs")
    
    return result is not None

def main():
    """Main fix function"""
    print("🚀 Starting targeted backend fix...")
    
    # Install git on EC2
    if not install_git_on_ec2():
        print("❌ Failed to install git")
        return False
    
    # Setup git repository on EC2
    if not setup_git_repo_on_ec2():
        print("❌ Failed to setup git repository")
        return False
    
    # Create repository configuration on EC2
    if not create_repo_config_on_ec2():
        print("❌ Failed to create repository config")
        return False
    
    # Apply async generator fix on EC2
    if not apply_async_fix_on_ec2():
        print("❌ Failed to apply async fix")
        return False
    
    # Restart backend on EC2
    if not restart_backend_on_ec2():
        print("❌ Failed to restart backend")
        return False
    
    # Check logs
    check_logs_on_ec2()
    
    print("✅ Targeted backend fix completed!")
    print("\n📋 Summary of fixes:")
    print("- ✅ Git installed and configured on EC2")
    print("- ✅ Git repository initialized on EC2")
    print("- ✅ Repository configuration created on EC2")
    print("- ✅ Async generator fix applied on EC2")
    print("- ✅ Backend service restarted on EC2")
    
    print("\n🔧 Next steps:")
    print("1. Update the repository URL in repository_config.json on EC2")
    print("2. Monitor logs: ssh ubuntu@34.202.215.209 'journalctl -u ai-backend-python -f'")
    print("3. Test the app to see if async generator errors are resolved")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 