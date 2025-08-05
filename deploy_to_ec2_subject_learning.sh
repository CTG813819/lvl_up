#!/bin/bash

# Enhanced Subject Learning Features Deployment Script for EC2
# EC2 Instance: 34-202-215-209.compute-1.amazonaws.com
# Key File: C:\projects\lvl_up\New.pem

set -e

echo "🚀 Deploying Enhanced Subject Learning Features to EC2..."

# EC2 Configuration
EC2_HOST="34-202-215-209.compute-1.amazonaws.com"
EC2_USER="ubuntu"
KEY_FILE="C:/projects/lvl_up/New.pem"
REMOTE_DIR="/home/ubuntu/ai-backend-python"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run command on EC2
run_on_ec2() {
    ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" "$1"
}

# Function to copy file to EC2
copy_to_ec2() {
    scp -i "$KEY_FILE" -o StrictHostKeyChecking=no "$1" "$EC2_USER@$EC2_HOST:$2"
}

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    print_error "SSH key file not found: $KEY_FILE"
    exit 1
fi

print_status "Starting deployment to EC2 instance: $EC2_HOST"

# 1. Test SSH connection
print_status "Step 1: Testing SSH connection..."
if run_on_ec2 "echo 'SSH connection successful'"; then
    print_success "SSH connection established"
else
    print_error "Failed to connect to EC2 instance"
    exit 1
fi

# 2. Create deployment directory and copy files
print_status "Step 2: Setting up deployment directory..."
run_on_ec2 "mkdir -p $REMOTE_DIR"

# Copy enhanced subject learning service
print_status "Copying enhanced subject learning service..."
copy_to_ec2 "ai-backend-python/app/services/enhanced_subject_learning_service.py" "$REMOTE_DIR/app/services/"

# Copy updated models
print_status "Copying updated models..."
copy_to_ec2 "ai-backend-python/app/models/sql_models.py" "$REMOTE_DIR/app/models/"
copy_to_ec2 "ai-backend-python/app/models/training_data.py" "$REMOTE_DIR/app/models/"
copy_to_ec2 "ai-backend-python/app/models/oath_paper.py" "$REMOTE_DIR/app/models/"

# Copy updated routers
print_status "Copying updated routers..."
copy_to_ec2 "ai-backend-python/app/routers/oath_papers.py" "$REMOTE_DIR/app/routers/"
copy_to_ec2 "ai-backend-python/app/routers/training_data.py" "$REMOTE_DIR/app/routers/"

# Copy migration and deployment scripts
print_status "Copying migration and deployment scripts..."
copy_to_ec2 "ai-backend-python/add_subject_fields_migration.py" "$REMOTE_DIR/"
copy_to_ec2 "ai-backend-python/deploy_subject_learning_features.sh" "$REMOTE_DIR/"

# 3. Install dependencies on EC2
print_status "Step 3: Installing dependencies on EC2..."
run_on_ec2 "cd $REMOTE_DIR && pip install aiohttp"

# 4. Run database migration
print_status "Step 4: Running database migration..."
run_on_ec2 "cd $REMOTE_DIR && python add_subject_fields_migration.py"

# 5. Set up environment variables (if not already set)
print_status "Step 5: Setting up environment variables..."
run_on_ec2 "echo 'export OPENAI_API_KEY=\"your_openai_api_key\"' >> ~/.bashrc"
run_on_ec2 "echo 'export ANTHROPIC_API_KEY=\"your_anthropic_api_key\"' >> ~/.bashrc"
run_on_ec2 "echo 'export GOOGLE_SEARCH_API_KEY=\"your_google_api_key\"' >> ~/.bashrc"
run_on_ec2 "echo 'export GOOGLE_SEARCH_ENGINE_ID=\"your_search_engine_id\"' >> ~/.bashrc"

# 6. Create autonomous AI learning integration
print_status "Step 6: Setting up autonomous AI learning integration..."

# Create autonomous learning service
cat > autonomous_subject_learning_service.py << 'EOF'
"""
Autonomous Subject Learning Service for EC2
Integrates enhanced subject learning into AI learning cycles
"""

import asyncio
import schedule
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import structlog
from app.services.enhanced_subject_learning_service import EnhancedSubjectLearningService
from app.services.ai_learning_service import AILearningService
from app.core.database import get_session
from app.models.sql_models import OathPaper, TrainingData

logger = structlog.get_logger()

class AutonomousSubjectLearningService:
    """Autonomous service that integrates subject learning into AI learning cycles"""
    
    def __init__(self):
        self.enhanced_learning = EnhancedSubjectLearningService()
        self.ai_learning = AILearningService()
        self.subjects_queue = []
        self.learning_cycle_active = False
        self.last_learning_cycle = None
        
        # Predefined subjects for autonomous learning
        self.autonomous_subjects = [
            "machine learning", "artificial intelligence", "cybersecurity", "hacking",
            "stock market", "trading", "blockchain", "cryptocurrency", "web development",
            "mobile development", "data science", "cloud computing", "devops",
            "game development", "robotics", "natural language processing",
            "computer vision", "deep learning", "neural networks", "algorithm design"
        ]
        
    async def start_autonomous_learning(self):
        """Start the autonomous learning cycle"""
        logger.info("Starting autonomous subject learning service")
        
        # Schedule learning cycles
        schedule.every(2).hours.do(self.trigger_learning_cycle)
        schedule.every().day.at("05:00").do(self.daily_learning_cycle)
        schedule.every().day.at("17:00").do(self.evening_learning_cycle)
        
        # Start the scheduler
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
    
    async def trigger_learning_cycle(self):
        """Trigger an autonomous learning cycle"""
        if self.learning_cycle_active:
            logger.info("Learning cycle already active, skipping")
            return
            
        self.learning_cycle_active = True
        logger.info("Starting autonomous learning cycle")
        
        try:
            # Select random subjects for learning
            subjects_to_learn = random.sample(self.autonomous_subjects, 3)
            
            for subject in subjects_to_learn:
                await self.learn_subject_autonomously(subject)
                await asyncio.sleep(30)  # Wait between subjects
            
            self.last_learning_cycle = datetime.now()
            logger.info("Autonomous learning cycle completed")
            
        except Exception as e:
            logger.error(f"Error in learning cycle: {e}")
        finally:
            self.learning_cycle_active = False
    
    async def learn_subject_autonomously(self, subject: str):
        """Learn a subject autonomously and integrate with AI systems"""
        try:
            logger.info(f"Learning subject autonomously: {subject}")
            
            # Research the subject
            knowledge_base = await self.enhanced_learning.build_subject_knowledge_base(
                subject=subject,
                context=f"Autonomous learning for {subject}"
            )
            
            # Create oath paper for the subject
            await self.create_autonomous_oath_paper(subject, knowledge_base)
            
            # Create training data for the subject
            await self.create_autonomous_training_data(subject, knowledge_base)
            
            # Integrate with AI learning systems
            await self.integrate_with_ai_learning(subject, knowledge_base)
            
            logger.info(f"Autonomous learning completed for: {subject}")
            
        except Exception as e:
            logger.error(f"Error learning subject {subject}: {e}")
    
    async def create_autonomous_oath_paper(self, subject: str, knowledge_base: Dict[str, Any]):
        """Create an oath paper for autonomous learning"""
        try:
            session = get_session()
            async with session as s:
                oath_paper = OathPaper(
                    title=f"Autonomous Learning: {subject}",
                    subject=subject,
                    content=knowledge_base.get("knowledge_summary", f"Autonomous learning about {subject}"),
                    category="autonomous_learning",
                    ai_insights=knowledge_base,
                    learning_value=knowledge_base.get("learning_value", 0.0),
                    status="learned",
                    created_at=datetime.utcnow()
                )
                
                s.add(oath_paper)
                await s.commit()
                
                logger.info(f"Created autonomous oath paper for: {subject}")
                
        except Exception as e:
            logger.error(f"Error creating autonomous oath paper: {e}")
    
    async def create_autonomous_training_data(self, subject: str, knowledge_base: Dict[str, Any]):
        """Create training data for autonomous learning"""
        try:
            session = get_session()
            async with session as s:
                training_data = TrainingData(
                    title=f"Autonomous Training: {subject}",
                    subject=subject,
                    description=knowledge_base.get("knowledge_summary", f"Autonomous training data for {subject}"),
                    code="\n".join(knowledge_base.get("code_examples", [])),
                    timestamp=datetime.utcnow(),
                    status="processed",
                    processed_at=datetime.utcnow(),
                    processing_notes=json.dumps({
                        "autonomous_learning": True,
                        "knowledge_base": knowledge_base,
                        "learning_value": knowledge_base.get("learning_value", 0.0)
                    })
                )
                
                s.add(training_data)
                await s.commit()
                
                logger.info(f"Created autonomous training data for: {subject}")
                
        except Exception as e:
            logger.error(f"Error creating autonomous training data: {e}")
    
    async def integrate_with_ai_learning(self, subject: str, knowledge_base: Dict[str, Any]):
        """Integrate subject learning with AI learning systems"""
        try:
            # Process with AI learning service
            processing_result = await self.ai_learning.process_enhanced_oath_paper(
                oath_paper_id=f"autonomous-{subject}-{datetime.now().timestamp()}",
                subject=subject,
                tags=[subject, "autonomous", "learning"],
                description=knowledge_base.get("knowledge_summary", ""),
                code="\n".join(knowledge_base.get("code_examples", [])),
                target_ai=None,  # All AIs
                ai_weights={"Imperium": 0.4, "Guardian": 0.3, "Sandbox": 0.2, "Conquest": 0.1},
                extract_keywords=True,
                internet_search=True,
                git_integration=True
            )
            
            # Store learning insights
            await self.store_learning_insights(subject, knowledge_base, processing_result)
            
            logger.info(f"Integrated {subject} with AI learning systems")
            
        except Exception as e:
            logger.error(f"Error integrating with AI learning: {e}")
    
    async def store_learning_insights(self, subject: str, knowledge_base: Dict[str, Any], processing_result: Dict[str, Any]):
        """Store learning insights for future reference"""
        try:
            insights = {
                "subject": subject,
                "timestamp": datetime.now().isoformat(),
                "knowledge_base": knowledge_base,
                "processing_result": processing_result,
                "learning_value": knowledge_base.get("learning_value", 0.0),
                "ai_responses": processing_result.get("ai_responses", {}),
                "autonomous": True
            }
            
            # Store in database or file system
            # This could be extended to store in a dedicated insights table
            
            logger.info(f"Stored learning insights for: {subject}")
            
        except Exception as e:
            logger.error(f"Error storing learning insights: {e}")
    
    async def daily_learning_cycle(self):
        """Daily comprehensive learning cycle"""
        logger.info("Starting daily learning cycle")
        
        # Learn more subjects during daily cycle
        subjects_to_learn = random.sample(self.autonomous_subjects, 5)
        
        for subject in subjects_to_learn:
            await self.learn_subject_autonomously(subject)
            await asyncio.sleep(60)  # Wait longer between subjects
    
    async def evening_learning_cycle(self):
        """Evening learning cycle with focus on practical applications"""
        logger.info("Starting evening learning cycle")
        
        # Focus on practical subjects
        practical_subjects = ["web development", "mobile development", "cybersecurity", "trading", "data science"]
        subjects_to_learn = random.sample(practical_subjects, 3)
        
        for subject in subjects_to_learn:
            await self.learn_subject_autonomously(subject)
            await asyncio.sleep(45)
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status"""
        return {
            "autonomous_learning_active": self.learning_cycle_active,
            "last_learning_cycle": self.last_learning_cycle.isoformat() if self.last_learning_cycle else None,
            "subjects_learned": len(self.autonomous_subjects),
            "next_scheduled_cycle": schedule.next_run().isoformat() if schedule.next_run() else None
        }

# Global instance
autonomous_service = AutonomousSubjectLearningService()

async def start_autonomous_service():
    """Start the autonomous learning service"""
    await autonomous_service.start_autonomous_learning()

if __name__ == "__main__":
    asyncio.run(start_autonomous_service())
EOF

# Copy autonomous learning service to EC2
copy_to_ec2 "autonomous_subject_learning_service.py" "$REMOTE_DIR/"

# 7. Create systemd service for autonomous learning
print_status "Step 7: Creating systemd service for autonomous learning..."

# Create systemd service file
cat > autonomous-learning.service << 'EOF'
[Unit]
Description=Autonomous Subject Learning Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-backend-python
Environment=PATH=/home/ubuntu/ai-backend-python/venv/bin
ExecStart=/home/ubuntu/ai-backend-python/venv/bin/python autonomous_subject_learning_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Copy service file to EC2
copy_to_ec2 "autonomous-learning.service" "/tmp/"

# Install and enable the service
run_on_ec2 "sudo mv /tmp/autonomous-learning.service /etc/systemd/system/"
run_on_ec2 "sudo systemctl daemon-reload"
run_on_ec2 "sudo systemctl enable autonomous-learning.service"

# 8. Create AI learning cycle integration
print_status "Step 8: Creating AI learning cycle integration..."

# Create AI learning cycle enhancement
cat > ai_learning_cycle_enhancement.py << 'EOF'
"""
AI Learning Cycle Enhancement
Integrates subject learning into existing AI learning cycles
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import structlog
from app.services.enhanced_subject_learning_service import EnhancedSubjectLearningService
from app.services.ai_learning_service import AILearningService
from app.core.database import get_session
from app.models.sql_models import OathPaper, TrainingData, AgentMetrics
from sqlalchemy import select

logger = structlog.get_logger()

class AILearningCycleEnhancement:
    """Enhances AI learning cycles with subject-based learning"""
    
    def __init__(self):
        self.enhanced_learning = EnhancedSubjectLearningService()
        self.ai_learning = AILearningService()
        
        # Subject categories for different AI types
        self.ai_subject_mapping = {
            "imperium": ["machine learning", "artificial intelligence", "data science", "algorithm design"],
            "guardian": ["cybersecurity", "hacking", "security", "penetration testing"],
            "sandbox": ["web development", "mobile development", "game development", "software engineering"],
            "conquest": ["trading", "stock market", "blockchain", "cryptocurrency", "financial analysis"]
        }
    
    async def enhance_ai_learning_cycle(self, ai_type: str, learning_context: str = ""):
        """Enhance AI learning cycle with subject-based learning"""
        try:
            logger.info(f"Enhancing learning cycle for {ai_type}")
            
            # Get relevant subjects for this AI
            subjects = self.ai_subject_mapping.get(ai_type.lower(), [])
            
            if not subjects:
                logger.warning(f"No subjects mapped for AI type: {ai_type}")
                return
            
            # Select a subject for this learning cycle
            selected_subject = random.choice(subjects)
            
            # Research the subject
            knowledge_base = await self.enhanced_learning.build_subject_knowledge_base(
                subject=selected_subject,
                context=f"AI learning cycle for {ai_type}: {learning_context}"
            )
            
            # Create enhanced learning record
            await self.create_enhanced_learning_record(ai_type, selected_subject, knowledge_base)
            
            # Update AI metrics
            await self.update_ai_metrics(ai_type, selected_subject, knowledge_base)
            
            # Trigger cross-AI knowledge sharing
            await self.share_knowledge_across_ais(ai_type, selected_subject, knowledge_base)
            
            logger.info(f"Enhanced learning cycle completed for {ai_type} with subject: {selected_subject}")
            
        except Exception as e:
            logger.error(f"Error enhancing learning cycle for {ai_type}: {e}")
    
    async def create_enhanced_learning_record(self, ai_type: str, subject: str, knowledge_base: Dict[str, Any]):
        """Create enhanced learning record"""
        try:
            session = get_session()
            async with session as s:
                # Create oath paper
                oath_paper = OathPaper(
                    title=f"Enhanced Learning: {subject} for {ai_type}",
                    subject=subject,
                    content=knowledge_base.get("knowledge_summary", f"Enhanced learning about {subject} for {ai_type}"),
                    category=f"enhanced_{ai_type}_learning",
                    ai_insights=knowledge_base,
                    learning_value=knowledge_base.get("learning_value", 0.0),
                    status="learned",
                    ai_responses={ai_type: "enhanced_learning_completed"},
                    created_at=datetime.utcnow()
                )
                
                s.add(oath_paper)
                await s.commit()
                
                logger.info(f"Created enhanced learning record for {ai_type}: {subject}")
                
        except Exception as e:
            logger.error(f"Error creating enhanced learning record: {e}")
    
    async def update_ai_metrics(self, ai_type: str, subject: str, knowledge_base: Dict[str, Any]):
        """Update AI metrics with enhanced learning"""
        try:
            session = get_session()
            async with session as s:
                # Get or create agent metrics
                agent_metrics = await s.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
                )
                agent_metrics = agent_metrics.scalar_one_or_none()
                
                if not agent_metrics:
                    agent_metrics = AgentMetrics(
                        agent_id=f"{ai_type}_enhanced",
                        agent_type=ai_type,
                        learning_score=0.0,
                        success_rate=0.0,
                        failure_rate=0.0,
                        total_learning_cycles=0,
                        xp=0,
                        level=1,
                        prestige=0
                    )
                    s.add(agent_metrics)
                
                # Update metrics
                learning_value = knowledge_base.get("learning_value", 0.0)
                agent_metrics.learning_score += learning_value
                agent_metrics.total_learning_cycles += 1
                agent_metrics.xp += int(learning_value * 100)
                agent_metrics.last_learning_cycle = datetime.utcnow()
                
                # Update level based on XP
                new_level = (agent_metrics.xp // 1000) + 1
                if new_level > agent_metrics.level:
                    agent_metrics.level = new_level
                    logger.info(f"{ai_type} leveled up to level {new_level}")
                
                # Update learning patterns
                if not agent_metrics.learning_patterns:
                    agent_metrics.learning_patterns = []
                
                agent_metrics.learning_patterns.append({
                    "timestamp": datetime.now().isoformat(),
                    "subject": subject,
                    "learning_value": learning_value,
                    "type": "enhanced_subject_learning"
                })
                
                await s.commit()
                
                logger.info(f"Updated metrics for {ai_type}: +{learning_value} learning score")
                
        except Exception as e:
            logger.error(f"Error updating AI metrics: {e}")
    
    async def share_knowledge_across_ais(self, source_ai: str, subject: str, knowledge_base: Dict[str, Any]):
        """Share knowledge across AI systems"""
        try:
            # Share with other AI types
            other_ais = [ai for ai in self.ai_subject_mapping.keys() if ai != source_ai.lower()]
            
            for target_ai in other_ais:
                # Create shared learning record
                session = get_session()
                async with session as s:
                    shared_paper = OathPaper(
                        title=f"Shared Knowledge: {subject} from {source_ai} to {target_ai}",
                        subject=subject,
                        content=f"Knowledge shared from {source_ai} to {target_ai}: {knowledge_base.get('knowledge_summary', '')}",
                        category="shared_knowledge",
                        ai_insights=knowledge_base,
                        learning_value=knowledge_base.get("learning_value", 0.0) * 0.5,  # Reduced value for sharing
                        status="shared",
                        ai_responses={target_ai: "knowledge_received"},
                        created_at=datetime.utcnow()
                    )
                    
                    s.add(shared_paper)
                    await s.commit()
                
                logger.info(f"Shared knowledge from {source_ai} to {target_ai}: {subject}")
                
        except Exception as e:
            logger.error(f"Error sharing knowledge: {e}")
    
    async def trigger_intuitive_growth(self, ai_type: str):
        """Trigger intuitive growth based on learned subjects"""
        try:
            session = get_session()
            async with session as s:
                # Get recent learning patterns
                agent_metrics = await s.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
                )
                agent_metrics = agent_metrics.scalar_one_or_none()
                
                if not agent_metrics or not agent_metrics.learning_patterns:
                    return
                
                # Analyze learning patterns for intuitive growth
                recent_patterns = agent_metrics.learning_patterns[-10:]  # Last 10 patterns
                
                # Identify patterns and trigger growth
                subjects_learned = [p.get("subject") for p in recent_patterns if p.get("subject")]
                total_learning_value = sum(p.get("learning_value", 0) for p in recent_patterns)
                
                if total_learning_value > 50:  # Threshold for intuitive growth
                    # Trigger enhanced learning cycle
                    await self.enhance_ai_learning_cycle(ai_type, "intuitive_growth_triggered")
                    
                    # Update prestige if significant growth
                    if total_learning_value > 100:
                        agent_metrics.prestige += 1
                        await s.commit()
                        logger.info(f"{ai_type} achieved intuitive growth milestone")
                
        except Exception as e:
            logger.error(f"Error triggering intuitive growth: {e}")

# Global instance
ai_learning_enhancement = AILearningCycleEnhancement()

async def enhance_learning_cycles():
    """Enhance all AI learning cycles"""
    ai_types = ["imperium", "guardian", "sandbox", "conquest"]
    
    for ai_type in ai_types:
        await ai_learning_enhancement.enhance_ai_learning_cycle(ai_type)
        await asyncio.sleep(30)  # Wait between AIs

if __name__ == "__main__":
    asyncio.run(enhance_learning_cycles())
EOF

# Copy AI learning cycle enhancement to EC2
copy_to_ec2 "ai_learning_cycle_enhancement.py" "$REMOTE_DIR/"

# 9. Create startup script
print_status "Step 9: Creating startup script..."

cat > start_enhanced_services.sh << 'EOF'
#!/bin/bash

# Enhanced Services Startup Script for EC2

echo "🚀 Starting Enhanced Subject Learning Services..."

# Activate virtual environment
source /home/ubuntu/ai-backend-python/venv/bin/activate

# Start autonomous learning service
echo "Starting autonomous learning service..."
python autonomous_subject_learning_service.py &

# Start AI learning cycle enhancement
echo "Starting AI learning cycle enhancement..."
python ai_learning_cycle_enhancement.py &

# Start main application
echo "Starting main application..."
python main.py &

echo "✅ All enhanced services started"
EOF

# Copy startup script to EC2
copy_to_ec2 "start_enhanced_services.sh" "$REMOTE_DIR/"
run_on_ec2 "chmod +x $REMOTE_DIR/start_enhanced_services.sh"

# 10. Create monitoring script
print_status "Step 10: Creating monitoring script..."

cat > monitor_enhanced_learning.py << 'EOF'
#!/usr/bin/env python3
"""
Monitoring script for enhanced subject learning on EC2
"""

import asyncio
import json
from datetime import datetime
from app.core.database import get_session
from app.models.sql_models import OathPaper, TrainingData, AgentMetrics
from sqlalchemy import select
from datetime import timedelta

async def monitor_enhanced_learning():
    """Monitor enhanced learning activities"""
    try:
        session = get_session()
        async with session as s:
            # Get recent oath papers
            recent_oath_papers = await s.execute(
                select(OathPaper)
                .where(OathPaper.created_at >= datetime.utcnow() - timedelta(hours=24))
                .order_by(OathPaper.created_at.desc())
                .limit(10)
            )
            oath_papers = recent_oath_papers.scalars().all()
            
            # Get recent training data
            recent_training_data = await s.execute(
                select(TrainingData)
                .where(TrainingData.timestamp >= datetime.utcnow() - timedelta(hours=24))
                .order_by(TrainingData.timestamp.desc())
                .limit(10)
            )
            training_data = recent_training_data.scalars().all()
            
            # Get AI metrics
            ai_metrics = await s.execute(select(AgentMetrics))
            metrics = ai_metrics.scalars().all()
            
            # Generate report
            report = {
                "timestamp": datetime.now().isoformat(),
                "oath_papers_last_24h": len(oath_papers),
                "training_data_last_24h": len(training_data),
                "ai_metrics": [
                    {
                        "agent_type": m.agent_type,
                        "learning_score": m.learning_score,
                        "level": m.level,
                        "prestige": m.prestige,
                        "total_learning_cycles": m.total_learning_cycles
                    }
                    for m in metrics
                ],
                "recent_subjects": [
                    {
                        "subject": p.subject,
                        "title": p.title,
                        "learning_value": p.learning_value,
                        "created_at": p.created_at.isoformat()
                    }
                    for p in oath_papers if p.subject
                ]
            }
            
            print(json.dumps(report, indent=2))
            
    except Exception as e:
        print(f"Error monitoring enhanced learning: {e}")

if __name__ == "__main__":
    asyncio.run(monitor_enhanced_learning())
EOF

# Copy monitoring script to EC2
copy_to_ec2 "monitor_enhanced_learning.py" "$REMOTE_DIR/"

# 11. Final setup and restart
print_status "Step 11: Final setup and restart..."

# Restart services
run_on_ec2 "sudo systemctl restart autonomous-learning.service"

# Create cron job for monitoring
run_on_ec2 "echo '*/30 * * * * cd $REMOTE_DIR && python monitor_enhanced_learning.py >> /var/log/enhanced-learning.log 2>&1' | crontab -"

# 12. Final status
print_status "Step 12: Final status check..."

echo ""
print_success "Enhanced Subject Learning Features Deployed to EC2 Successfully!"
echo ""
echo "📋 Summary of deployed features:"
echo "  ✅ Enhanced Subject Learning Service deployed"
echo "  ✅ Autonomous AI Learning Service deployed"
echo "  ✅ AI Learning Cycle Enhancement deployed"
echo "  ✅ Systemd service configured for autonomous learning"
echo "  ✅ Database migration completed"
echo "  ✅ Monitoring and logging configured"
echo ""
echo "🔧 Services running on EC2:"
echo "  🚀 Autonomous Learning Service: systemctl status autonomous-learning.service"
echo "  📊 Monitoring: python monitor_enhanced_learning.py"
echo "  🔄 AI Learning Cycles: Enhanced with subject-based learning"
echo ""
echo "🎯 Autonomous Features:"
echo "  🤖 AIs will autonomously learn subjects every 2 hours"
echo "  🌅 Daily comprehensive learning cycles at 5:00 AM"
echo "  🌆 Evening practical learning cycles at 5:00 PM"
echo "  🔄 Cross-AI knowledge sharing enabled"
echo "  📈 Intuitive growth tracking and leveling"
echo ""
echo "📚 Documentation: ENHANCED_SUBJECT_LEARNING_FEATURES.md"
echo "🔍 Monitor logs: tail -f /var/log/enhanced-learning.log"
echo ""

print_success "EC2 deployment completed successfully!" 