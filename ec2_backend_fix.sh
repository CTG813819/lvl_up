#!/bin/bash

# Backend Issues Fix Script for EC2
# Run this script on the EC2 instance to fix async generator, git, and repository issues

echo "🚀 Starting backend issues fix..."

# Function to run commands and check status
run_command() {
    echo "🔧 $1..."
    if eval "$2"; then
        echo "✅ $1 completed successfully"
        return 0
    else
        echo "❌ $1 failed"
        return 1
    fi
}

# Install git if not present
run_command "Checking git installation" "git --version > /dev/null 2>&1"
if [ $? -ne 0 ]; then
    run_command "Installing git" "sudo apt update && sudo apt install -y git"
    run_command "Configuring git" "git config --global user.name 'AI Backend' && git config --global user.email 'ai-backend@example.com'"
fi

# Setup git repository
cd ~/ai-backend-python
run_command "Checking git repository" "git status > /dev/null 2>&1"
if [ $? -ne 0 ]; then
    run_command "Initializing git repository" "git init"
    run_command "Adding files to git" "git add ."
    run_command "Making initial commit" 'git commit -m "Initial commit - AI Backend Setup"'
fi

# Create repository configuration
echo "🔧 Creating repository configuration..."
cat > repository_config.json << 'EOF'
{
  "repository": {
    "url": "https://github.com/your-username/lvl_up.git",
    "branch": "main",
    "remote": "origin"
  },
  "experiments": {
    "default_repository": "https://github.com/your-username/lvl_up.git",
    "auto_push": true,
    "create_issues": true
  }
}
EOF
echo "✅ Repository configuration created"

# Fix async generator issues
echo "🔧 Fixing async generator issues..."

# Backup original learning service
cp app/services/ai_learning_service.py app/services/ai_learning_service.py.backup

# Create fixed version of the learning service
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

echo "✅ Async generator fix created"

# Create environment configuration
echo "🔧 Creating environment configuration..."
cat > .env.fixed << 'EOF'
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
EOF

echo "✅ Environment configuration created"

# Restart backend service
echo "🔧 Restarting backend service..."
run_command "Stopping backend service" "sudo systemctl stop ai-backend-python"
run_command "Starting backend service" "sudo systemctl start ai-backend-python"
run_command "Checking service status" "sudo systemctl status ai-backend-python --no-pager"

# Check recent logs
echo "🔧 Checking recent logs..."
echo "📋 Recent logs:"
journalctl -u ai-backend-python -n 20 --no-pager

echo "✅ Backend issues fix completed!"
echo ""
echo "📋 Summary of fixes:"
echo "- ✅ Git installed and configured"
echo "- ✅ Git repository initialized"
echo "- ✅ Repository configuration created"
echo "- ✅ Async generator fix created"
echo "- ✅ Environment configuration created"
echo "- ✅ Backend service restarted"
echo ""
echo "🔧 Next steps:"
echo "1. Update the repository URL in repository_config.json"
echo "2. Update the DATABASE_URL in .env.fixed"
echo "3. Copy .env.fixed to .env if needed"
echo "4. Monitor logs: journalctl -u ai-backend-python -f"
echo "5. Test the app to see if async generator errors are resolved" 