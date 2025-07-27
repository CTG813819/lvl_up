#!/usr/bin/env python3
"""
Fix Systemd Services - Create separate Python scripts for each AI agent
"""

import os

def create_imperium_script():
    """Create Imperium AI script"""
    script = '''#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def run_imperium():
    try:
        from app.services.ai_agent_service import AIAgentService
        service = AIAgentService()
        while True:
            print("Running Imperium AI testing...")
            await service.run_imperium_testing(threshold=0.92)
            await asyncio.sleep(2700)  # 45 minutes
    except Exception as e:
        print(f"Imperium error: {e}")
        await asyncio.sleep(60)  # Wait before retry

if __name__ == "__main__":
    asyncio.run(run_imperium())
'''
    
    with open("imperium_runner.py", 'w') as f:
        f.write(script)
    os.chmod("imperium_runner.py", 0o755)

def create_sandbox_script():
    """Create Sandbox AI script"""
    script = '''#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def run_sandbox():
    try:
        from app.services.ai_agent_service import AIAgentService
        service = AIAgentService()
        while True:
            print("Running Sandbox experimentation...")
            await service.run_sandbox_experimentation(quality_threshold=0.85, new_code_only=True)
            await asyncio.sleep(2700)  # 45 minutes
    except Exception as e:
        print(f"Sandbox error: {e}")
        await asyncio.sleep(60)  # Wait before retry

if __name__ == "__main__":
    asyncio.run(run_sandbox())
'''
    
    with open("sandbox_runner.py", 'w') as f:
        f.write(script)
    os.chmod("sandbox_runner.py", 0o755)

def create_custodes_script():
    """Create Custodes AI script"""
    script = '''#!/usr/bin/env python3
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def run_custodes():
    try:
        from app.services.ai_agent_service import AIAgentService
        service = AIAgentService()
        counter = 0
        while True:
            if counter % 2 == 0:
                print("Running comprehensive Custodes testing...")
                await service.run_comprehensive_custodes_testing()
            else:
                print("Running regular Custodes testing...")
                await service.run_custodes_testing()
            counter += 1
            await asyncio.sleep(2700)  # 45 minutes
    except Exception as e:
        print(f"Custodes error: {e}")
        await asyncio.sleep(60)  # Wait before retry

if __name__ == "__main__":
    asyncio.run(run_custodes())
'''
    
    with open("custodes_runner.py", 'w') as f:
        f.write(script)
    os.chmod("custodes_runner.py", 0o755)

def create_guardian_script():
    """Create Guardian AI script"""
    script = '''#!/usr/bin/env python3
import asyncio
import sys
import os
import json
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

async def run_guardian():
    try:
        from app.services.ai_agent_service import AIAgentService
        from app.models.sql_models import Proposal
        from app.core.database import get_db
        
        service = AIAgentService()
        
        while True:
            print("Running Guardian system health check...")
            
            # Perform system health monitoring
            health_status = await service.monitor_system_health()
            
            if health_status.get('issues_detected', False):
                # Issues found - create healing proposal
                issues = health_status.get('issues', [])
                proposed_actions = health_status.get('proposed_actions', [])
                
                print(f"🔍 Guardian detected {len(issues)} system issues")
                
                # Create detailed proposal for user approval
                proposal_data = {
                    "title": f"Guardian Self-Healing Proposal - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "description": "Guardian AI has detected system issues requiring sudo privileges for resolution",
                    "ai_type": "guardian",
                    "proposal_type": "system_healing",
                    "content": {
                        "issues_detected": issues,
                        "proposed_actions": proposed_actions,
                        "sudo_required": True,
                        "risk_assessment": health_status.get('risk_assessment', 'Low'),
                        "estimated_downtime": health_status.get('estimated_downtime', 'None'),
                        "backup_plan": health_status.get('backup_plan', 'System state will be preserved')
                    },
                    "status": "pending_user_approval",
                    "priority": "high" if health_status.get('risk_assessment') == 'High' else "medium"
                }
                
                # Save proposal to database
                async with get_db() as db:
                    proposal = Proposal(
                        title=proposal_data["title"],
                        description=proposal_data["description"],
                        ai_type=proposal_data["ai_type"],
                        proposal_type=proposal_data["proposal_type"],
                        content=json.dumps(proposal_data["content"]),
                        status=proposal_data["status"],
                        priority=proposal_data["priority"]
                    )
                    db.add(proposal)
                    await db.commit()
                    await db.refresh(proposal)
                
                print(f"📋 Created healing proposal #{proposal.id} for user approval")
                print("Issues detected:")
                for issue in issues:
                    print(f"  • {issue}")
                print("Proposed actions:")
                for action in proposed_actions:
                    print(f"  • {action}")
                
                # Wait for user approval (check proposal status)
                approval_wait_time = 0
                max_wait_time = 3600  # 1 hour max wait
                
                while approval_wait_time < max_wait_time:
                    await asyncio.sleep(60)  # Check every minute
                    approval_wait_time += 60
                    
                    # Check if proposal was approved
                    async with get_db() as db:
                        updated_proposal = await db.get(Proposal, proposal.id)
                        if updated_proposal and updated_proposal.status == "approved":
                            print("✅ User approved healing proposal - executing actions...")
                            
                            # Execute the healing actions with sudo
                            healing_result = await service.execute_guardian_healing(
                                actions=proposed_actions,
                                sudo_required=True
                            )
                            
                            # Update proposal with results
                            updated_proposal.status = "completed"
                            updated_proposal.content = json.dumps({
                                **json.loads(updated_proposal.content),
                                "execution_results": healing_result,
                                "completed_at": datetime.now().isoformat()
                            })
                            await db.commit()
                            
                            print("✅ Guardian healing completed successfully")
                            break
                        elif updated_proposal and updated_proposal.status == "rejected":
                            print("❌ User rejected healing proposal")
                            break
                
                if approval_wait_time >= max_wait_time:
                    print("⏰ Healing proposal timed out - will retry in next cycle")
                    
            else:
                print("✅ System health check passed - no issues detected")
            
            # Wait for next health check cycle
            await asyncio.sleep(3600)  # 60 minutes
            
    except Exception as e:
        print(f"Guardian error: {e}")
        await asyncio.sleep(60)  # Wait before retry

if __name__ == "__main__":
    asyncio.run(run_guardian())
'''
    
    with open("guardian_runner.py", 'w') as f:
        f.write(script)
    os.chmod("guardian_runner.py", 0o755)

def create_fixed_systemd_services():
    """Create fixed systemd service files"""
    
    # Imperium service
    imperium_service = '''[Unit]
Description=Imperium AI Enhanced Testing Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python3 /home/ubuntu/ai-backend-python/imperium_runner.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
    
    with open("imperium-ai-fixed.service", 'w') as f:
        f.write(imperium_service)
    
    # Sandbox service
    sandbox_service = '''[Unit]
Description=Sandbox AI Experimentation Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python3 /home/ubuntu/ai-backend-python/sandbox_runner.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
    
    with open("sandbox-ai-fixed.service", 'w') as f:
        f.write(sandbox_service)
    
    # Custodes service
    custodes_service = '''[Unit]
Description=Custodes AI Testing Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python3 /home/ubuntu/ai-backend-python/custodes_runner.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
    
    with open("custodes-ai-fixed.service", 'w') as f:
        f.write(custodes_service)
    
    # Guardian service
    guardian_service = '''[Unit]
Description=Guardian AI Self-Healing Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python3 /home/ubuntu/ai-backend-python/guardian_runner.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
    
    with open("guardian-ai-fixed.service", 'w') as f:
        f.write(guardian_service)

def create_fixed_deployment_script():
    """Create fixed deployment script"""
    deployment_script = '''#!/bin/bash
# Fixed Enhanced AI System V2 Deployment Script
echo "🚀 Deploying Fixed Enhanced AI System V2..."

# Stop existing services
echo "🛑 Stopping existing services..."
sudo systemctl stop imperium-ai.service 2>/dev/null || true
sudo systemctl stop sandbox-ai.service 2>/dev/null || true
sudo systemctl stop custodes-ai.service 2>/dev/null || true
sudo systemctl stop guardian-ai.service 2>/dev/null || true

# Disable old services
sudo systemctl disable imperium-ai.service 2>/dev/null || true
sudo systemctl disable sandbox-ai.service 2>/dev/null || true
sudo systemctl disable custodes-ai.service 2>/dev/null || true
sudo systemctl disable guardian-ai.service 2>/dev/null || true

# Remove old service files
sudo rm -f /etc/systemd/system/imperium-ai.service
sudo rm -f /etc/systemd/system/sandbox-ai.service
sudo rm -f /etc/systemd/system/custodes-ai.service
sudo rm -f /etc/systemd/system/guardian-ai.service

# Copy fixed service files
echo "📋 Installing fixed systemd services..."
sudo cp imperium-ai-fixed.service /etc/systemd/system/imperium-ai.service
sudo cp sandbox-ai-fixed.service /etc/systemd/system/sandbox-ai.service
sudo cp custodes-ai-fixed.service /etc/systemd/system/custodes-ai.service
sudo cp guardian-ai-fixed.service /etc/systemd/system/guardian-ai.service

# Reload systemd
sudo systemctl daemon-reload

# Enable services
echo "✅ Enabling services..."
sudo systemctl enable imperium-ai.service
sudo systemctl enable sandbox-ai.service
sudo systemctl enable custodes-ai.service
sudo systemctl enable guardian-ai.service

# Start services
echo "🚀 Starting services..."
sudo systemctl start imperium-ai.service
sudo systemctl start sandbox-ai.service
sudo systemctl start custodes-ai.service
sudo systemctl start guardian-ai.service

# Check status
echo "📊 Service Status:"
sudo systemctl status imperium-ai.service --no-pager -l
sudo systemctl status sandbox-ai.service --no-pager -l
sudo systemctl status custodes-ai.service --no-pager -l
sudo systemctl status guardian-ai.service --no-pager -l

echo "✅ Fixed Enhanced AI System V2 deployed successfully!"
echo ""
echo "📋 Configuration Summary:"
echo "• Imperium: 92% testing threshold, every 45 minutes"
echo "• Sandbox: 85% quality threshold, new code only, every 45 minutes"
echo "• Custodes: Comprehensive testing every 90 minutes, regular every 45 minutes"
echo "• Guardian: Self-healing every 60 minutes with sudo approval"
echo "• Autonomous Learning: 40+ AI-specific sources with daily additions"
echo ""
echo "🔍 Monitor logs with:"
echo "sudo journalctl -u imperium-ai.service -f"
echo "sudo journalctl -u sandbox-ai.service -f"
echo "sudo journalctl -u custodes-ai.service -f"
echo "sudo journalctl -u guardian-ai.service -f"
'''
    
    with open("deploy_fixed_enhanced_ai_v2.sh", 'w') as f:
        f.write(deployment_script)
    os.chmod("deploy_fixed_enhanced_ai_v2.sh", 0o755)

def main():
    """Main function"""
    print("🔧 Creating fixed systemd services...")
    
    # Create Python runner scripts
    create_imperium_script()
    create_sandbox_script()
    create_custodes_script()
    create_guardian_script()
    
    # Create fixed systemd services
    create_fixed_systemd_services()
    
    # Create fixed deployment script
    create_fixed_deployment_script()
    
    print("✅ Fixed systemd services created!")
    print("📁 Files created:")
    print("• imperium_runner.py")
    print("• sandbox_runner.py")
    print("• custodes_runner.py")
    print("• guardian_runner.py")
    print("• imperium-ai-fixed.service")
    print("• sandbox-ai-fixed.service")
    print("• custodes-ai-fixed.service")
    print("• guardian-ai-fixed.service")
    print("• deploy_fixed_enhanced_ai_v2.sh")
    print("\n🚀 Next steps:")
    print("1. Run: chmod +x deploy_fixed_enhanced_ai_v2.sh")
    print("2. Run: ./deploy_fixed_enhanced_ai_v2.sh")

if __name__ == "__main__":
    main() 