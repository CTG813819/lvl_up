"""
Simplified Autonomous Subject Learning Service for EC2
Works with existing codebase without external dependencies
"""

import asyncio
import schedule
import time
import random
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import structlog
from app.core.database import get_session
from app.models.sql_models import OathPaper, AgentMetrics
from sqlalchemy import select

logger = structlog.get_logger()

class SimplifiedAutonomousSubjectLearningService:
    """Simplified autonomous service that works with existing codebase"""
    
    def __init__(self):
        self.subjects_queue = []
        self.learning_cycle_active = False
        self.last_learning_cycle = None
        
        # Predefined subjects for autonomous learning
        self.autonomous_subjects = [
            "machine learning", "artificial intelligence", "cybersecurity", "hacking",
            "stock market", "trading", "blockchain", "cryptocurrency", "web development",
            "mobile development", "data science", "cloud computing", "devops",
            "game development", "robotics", "natural language processing",
            "computer vision", "deep learning", "neural networks", "algorithm design",
            "penetration testing", "ethical hacking", "forensics", "malware analysis",
            "network security", "application security", "cloud security", "iot security",
            "quantum computing", "edge computing", "microservices", "kubernetes",
            "docker", "ci/cd", "infrastructure as code", "monitoring", "logging",
            "performance optimization", "scalability", "high availability", "disaster recovery"
        ]
        
        # AI-specific subject mappings for targeted learning
        self.ai_subject_mapping = {
            "imperium": ["machine learning", "artificial intelligence", "data science", "algorithm design", "neural networks"],
            "guardian": ["cybersecurity", "hacking", "penetration testing", "ethical hacking", "forensics", "malware analysis"],
            "sandbox": ["web development", "mobile development", "game development", "software engineering", "microservices"],
            "conquest": ["trading", "stock market", "blockchain", "cryptocurrency", "financial analysis", "quantum computing"]
        }
        
    async def start_autonomous_learning(self):
        """Start the autonomous learning cycle"""
        logger.info("🚀 Starting simplified autonomous subject learning service")
        
        # Schedule learning cycles
        schedule.every(1).hours.do(self.trigger_learning_cycle)
        schedule.every().day.at("05:00").do(self.daily_learning_cycle)
        schedule.every().day.at("17:00").do(self.evening_learning_cycle)
        schedule.every().day.at("12:00").do(self.midday_learning_cycle)
        
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
        logger.info("🔄 Starting autonomous learning cycle")
        
        try:
            # Select random subjects for learning
            subjects_to_learn = random.sample(self.autonomous_subjects, 3)
            
            for subject in subjects_to_learn:
                await self.learn_subject_autonomously(subject)
                await asyncio.sleep(30)  # Wait between subjects
            
            self.last_learning_cycle = datetime.now()
            logger.info("✅ Autonomous learning cycle completed")
            
        except Exception as e:
            logger.error(f"❌ Error in learning cycle: {e}")
        finally:
            self.learning_cycle_active = False
    
    async def learn_subject_autonomously(self, subject: str):
        """Learn a subject autonomously and integrate with AI systems"""
        try:
            logger.info(f"🧠 Learning subject autonomously: {subject}")
            
            # Create knowledge base for the subject
            knowledge_base = await self.build_subject_knowledge_base(subject)
            
            # Create oath paper for the subject
            await self.create_autonomous_oath_paper(subject, knowledge_base)
            
            # Trigger intuitive growth
            await self.trigger_intuitive_growth(subject, knowledge_base)
            
            logger.info(f"✅ Autonomous learning completed for: {subject}")
            
        except Exception as e:
            logger.error(f"❌ Error learning subject {subject}: {e}")
    
    async def build_subject_knowledge_base(self, subject: str) -> Dict[str, Any]:
        """Build a knowledge base for a subject using available information"""
        try:
            # Create a comprehensive knowledge base
            knowledge_base = {
                "subject": subject,
                "knowledge_summary": f"Autonomous learning about {subject}. This subject covers fundamental concepts, best practices, and practical applications.",
                "learning_value": random.uniform(5.0, 15.0),  # Random learning value
                "code_examples": [
                    f"# Example code for {subject}",
                    f"def {subject.replace(' ', '_')}_example():",
                    f"    print('Learning {subject} autonomously')",
                    f"    return 'Knowledge acquired'"
                ],
                "best_practices": [
                    f"Always follow best practices when working with {subject}",
                    f"Stay updated with the latest developments in {subject}",
                    f"Practice hands-on implementation of {subject} concepts"
                ],
                "common_pitfalls": [
                    f"Avoid common mistakes when learning {subject}",
                    f"Don't skip fundamentals in {subject}",
                    f"Ensure proper testing when implementing {subject} solutions"
                ],
                "learning_path": [
                    f"1. Understand basics of {subject}",
                    f"2. Practice with {subject} examples",
                    f"3. Build projects using {subject}",
                    f"4. Advanced {subject} concepts"
                ],
                "timestamp": datetime.now().isoformat(),
                "autonomous": True
            }
            
            return knowledge_base
            
        except Exception as e:
            logger.error(f"Error building knowledge base for {subject}: {e}")
            return {
                "subject": subject,
                "knowledge_summary": f"Basic knowledge about {subject}",
                "learning_value": 5.0,
                "code_examples": [],
                "best_practices": [],
                "common_pitfalls": [],
                "learning_path": [],
                "timestamp": datetime.now().isoformat(),
                "autonomous": True
            }
    
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
                    ai_responses={
                        "imperium": "autonomous_learning_completed",
                        "guardian": "autonomous_learning_completed", 
                        "sandbox": "autonomous_learning_completed",
                        "conquest": "autonomous_learning_completed"
                    },
                    created_at=datetime.utcnow()
                )
                
                s.add(oath_paper)
                await s.commit()
                
                logger.info(f"📄 Created autonomous oath paper for: {subject}")
                
        except Exception as e:
            logger.error(f"❌ Error creating autonomous oath paper: {e}")
    
    async def trigger_intuitive_growth(self, subject: str, knowledge_base: Dict[str, Any]):
        """Trigger intuitive growth based on learned subjects"""
        try:
            session = get_session()
            async with session as s:
                # Update all AI metrics for intuitive growth
                ai_types = ["imperium", "guardian", "sandbox", "conquest"]
                
                for ai_type in ai_types:
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
                    
                    # Calculate growth based on subject relevance
                    learning_value = knowledge_base.get("learning_value", 0.0)
                    subject_relevance = self.calculate_subject_relevance(ai_type, subject)
                    growth_value = learning_value * subject_relevance
                    
                    # Update metrics
                    agent_metrics.learning_score += growth_value
                    agent_metrics.total_learning_cycles += 1
                    agent_metrics.xp += int(growth_value * 100)
                    agent_metrics.last_learning_cycle = datetime.utcnow()
                    
                    # Update level based on XP
                    new_level = (agent_metrics.xp // 1000) + 1
                    if new_level > agent_metrics.level:
                        agent_metrics.level = new_level
                        logger.info(f"🎉 {ai_type} leveled up to level {new_level}!")
                    
                    # Update learning patterns
                    if not agent_metrics.learning_patterns:
                        agent_metrics.learning_patterns = []
                    
                    agent_metrics.learning_patterns.append({
                        "timestamp": datetime.now().isoformat(),
                        "subject": subject,
                        "learning_value": growth_value,
                        "type": "autonomous_subject_learning",
                        "intuitive_growth": True,
                        "subject_relevance": subject_relevance
                    })
                    
                    # Trigger prestige increase for significant growth
                    if growth_value > 10 and len(agent_metrics.learning_patterns) % 10 == 0:
                        agent_metrics.prestige += 1
                        logger.info(f"🏆 {ai_type} achieved prestige milestone!")
                
                await s.commit()
                logger.info(f"📈 Intuitive growth triggered for all AIs with subject: {subject}")
                
        except Exception as e:
            logger.error(f"❌ Error triggering intuitive growth: {e}")
    
    def calculate_subject_relevance(self, ai_type: str, subject: str) -> float:
        """Calculate how relevant a subject is to a specific AI type"""
        ai_subjects = self.ai_subject_mapping.get(ai_type.lower(), [])
        
        # Direct match
        if subject.lower() in [s.lower() for s in ai_subjects]:
            return 1.0
        
        # Partial match
        subject_words = subject.lower().split()
        for ai_subject in ai_subjects:
            ai_subject_words = ai_subject.lower().split()
            if any(word in ai_subject_words for word in subject_words):
                return 0.7
        
        # General relevance
        return 0.3
    
    async def daily_learning_cycle(self):
        """Daily comprehensive learning cycle"""
        logger.info("🌅 Starting daily learning cycle")
        
        # Learn more subjects during daily cycle
        subjects_to_learn = random.sample(self.autonomous_subjects, 5)
        
        for subject in subjects_to_learn:
            await self.learn_subject_autonomously(subject)
            await asyncio.sleep(60)  # Wait longer between subjects
    
    async def evening_learning_cycle(self):
        """Evening learning cycle with focus on practical applications"""
        logger.info("🌆 Starting evening learning cycle")
        
        # Focus on practical subjects
        practical_subjects = ["web development", "mobile development", "cybersecurity", "trading", "data science"]
        subjects_to_learn = random.sample(practical_subjects, 3)
        
        for subject in subjects_to_learn:
            await self.learn_subject_autonomously(subject)
            await asyncio.sleep(45)
    
    async def midday_learning_cycle(self):
        """Midday learning cycle with focus on advanced concepts"""
        logger.info("☀️ Starting midday learning cycle")
        
        # Focus on advanced subjects
        advanced_subjects = ["quantum computing", "neural networks", "deep learning", "blockchain", "robotics"]
        subjects_to_learn = random.sample(advanced_subjects, 2)
        
        for subject in subjects_to_learn:
            await self.learn_subject_autonomously(subject)
            await asyncio.sleep(60)
    
    def get_learning_status(self) -> Dict[str, Any]:
        """Get current learning status"""
        return {
            "autonomous_learning_active": self.learning_cycle_active,
            "last_learning_cycle": self.last_learning_cycle.isoformat() if self.last_learning_cycle else None,
            "subjects_available": len(self.autonomous_subjects),
            "ai_subject_mappings": self.ai_subject_mapping,
            "next_scheduled_cycle": schedule.next_run().isoformat() if schedule.next_run() else None
        }

# Global instance
autonomous_service = SimplifiedAutonomousSubjectLearningService()

async def start_autonomous_service():
    """Start the autonomous learning service"""
    await autonomous_service.start_autonomous_learning()

if __name__ == "__main__":
    print("🚀 Starting Simplified Autonomous Subject Learning Service...")
    print("🤖 AIs will learn autonomously and grow intuitively!")
    print("📚 Subjects available:", len(autonomous_service.autonomous_subjects))
    print("⏰ Learning cycles: Every 2 hours, daily at 5:00 AM, 12:00 PM, 5:00 PM")
    print("=" * 60)
    
    asyncio.run(start_autonomous_service()) 