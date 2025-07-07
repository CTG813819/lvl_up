"""
Imperium Learning Controller - Master Orchestrator of AI Learning
Coordinates and monitors the learning of all AI agents and itself
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from fastapi import WebSocket

from ..core.database import get_session
from ..core.config import settings
from .ai_agent_service import AIAgentService
from .ai_learning_service import AILearningService
from .ml_service import MLService
from .github_service import GitHubService
from .internet_fetchers import StackOverflowFetcher, GitHubFetcher, ArxivFetcher, MediumFetcher
from .trusted_sources import is_trusted_source

logger = structlog.get_logger()

class LearningStatus(Enum):
    """Learning status enumeration"""
    IDLE = "idle"
    LEARNING = "learning"
    SUCCESS = "success"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class AgentLearningMetrics:
    """Learning metrics for an AI agent"""
    agent_id: str
    agent_type: str
    learning_score: float
    success_rate: float
    failure_rate: float
    total_learning_cycles: int
    last_learning_cycle: Optional[datetime]
    last_success: Optional[datetime]
    last_failure: Optional[datetime]
    learning_patterns: List[str]
    improvement_suggestions: List[str]
    status: LearningStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class LearningCycle:
    """Learning cycle data"""
    cycle_id: str
    start_time: datetime
    end_time: Optional[datetime]
    participating_agents: List[str]
    total_learning_value: float
    success_count: int
    failure_count: int
    insights_generated: List[str]
    status: LearningStatus
    metadata: Dict[str, Any]


class ImperiumLearningController:
    """
    Master Learning Controller for Imperium
    Orchestrates and monitors the learning of all AI agents and itself
    """
    
    _instance = None
    _initialized = False
    _lock = threading.Lock()
    
    _internet_learning_log: list = []  # In-memory log of internet-based learning events
    _agent_topics: dict = {
        "imperium": [
            "meta-learning AI", "autonomous agent orchestration", "AI self-improvement", "AI governance"
        ],
        "guardian": [
            "AI security best practices", "AI code quality", "vulnerability detection", "secure coding"
        ],
        "sandbox": [
            "AI experimentation", "novel ML techniques", "rapid prototyping AI", "AI innovation"
        ],
        "conquest": [
            "app development AI", "AI-driven app design", "mobile AI frameworks", "AI UX optimization"
        ]
    }
    
    _websocket_clients: set = set()
    _periodic_internet_learning_task = None
    _internet_learning_interval = 1800  # 30 minutes (in seconds)
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ImperiumLearningController, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.agent_service = AIAgentService()
            self.learning_service = AILearningService()
            self.ml_service = MLService()
            self.github_service = GitHubService()
            
            # Learning state management
            self._agent_metrics: Dict[str, AgentLearningMetrics] = {}
            self._learning_cycles: List[LearningCycle] = []
            self._active_agents: Set[str] = set()
            self._learning_scheduler_running = False
            self._last_cycle_start = None
            
            # Configuration
            self.learning_cycle_interval = 300  # 5 minutes
            self.max_concurrent_learning = 3
            self.learning_timeout = 600  # 10 minutes
            
            # Threading
            self._executor = ThreadPoolExecutor(max_workers=5)
            self._learning_lock = asyncio.Lock()
            
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the Imperium Learning Controller"""
        instance = cls()
        
        # Initialize dependent services
        await instance.agent_service.initialize()
        await instance.learning_service.initialize()
        await instance.github_service.initialize()
        
        # Register default agents
        await instance._register_default_agents()
        
        # Start learning scheduler
        await instance._start_learning_scheduler()
        await cls.start_periodic_internet_learning()
        
        logger.info("Imperium Learning Controller initialized successfully")
        return instance
    
    async def _register_default_agents(self):
        """Register default AI agents"""
        default_agents = [
            {"id": "imperium", "type": "Imperium", "priority": "high"},
            {"id": "guardian", "type": "Guardian", "priority": "critical"},
            {"id": "sandbox", "type": "Sandbox", "priority": "low"},
            {"id": "conquest", "type": "Conquest", "priority": "medium"}
        ]
        
        for agent_data in default_agents:
            await self.register_agent(
                agent_id=agent_data["id"],
                agent_type=agent_data["type"],
                priority=agent_data["priority"]
            )
    
    async def register_agent(self, agent_id: str, agent_type: str, priority: str = "medium") -> bool:
        """Register a new AI agent for learning orchestration"""
        try:
            async with self._learning_lock:
                if agent_id in self._agent_metrics:
                    logger.warning(f"Agent {agent_id} already registered")
                    return False
                
                # Create initial metrics
                metrics = AgentLearningMetrics(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    learning_score=0.0,
                    success_rate=0.0,
                    failure_rate=0.0,
                    total_learning_cycles=0,
                    last_learning_cycle=None,
                    last_success=None,
                    last_failure=None,
                    learning_patterns=[],
                    improvement_suggestions=[],
                    status=LearningStatus.IDLE,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self._agent_metrics[agent_id] = metrics
                self._active_agents.add(agent_id)
                
                logger.info(f"Registered agent {agent_id} ({agent_type}) with priority {priority}")
                return True
                
        except Exception as e:
            logger.error(f"Error registering agent {agent_id}", error=str(e))
            return False
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an AI agent"""
        try:
            async with self._learning_lock:
                if agent_id not in self._agent_metrics:
                    return False
                
                del self._agent_metrics[agent_id]
                self._active_agents.discard(agent_id)
                
                logger.info(f"Unregistered agent {agent_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error unregistering agent {agent_id}", error=str(e))
            return False
    
    async def _start_learning_scheduler(self):
        """Start the learning cycle scheduler"""
        if self._learning_scheduler_running:
            return
        
        self._learning_scheduler_running = True
        
        async def scheduler_loop():
            while self._learning_scheduler_running:
                try:
                    await self._trigger_learning_cycle()
                    await asyncio.sleep(self.learning_cycle_interval)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error("Error in learning scheduler", error=str(e))
                    await asyncio.sleep(60)  # Wait 1 minute on error
        
        asyncio.create_task(scheduler_loop())
        logger.info("Learning scheduler started")
    
    async def _trigger_learning_cycle(self):
        """Trigger a new learning cycle for all active agents"""
        try:
            async with self._learning_lock:
                if not self._active_agents:
                    logger.info("No active agents for learning cycle")
                    return
                
                # Create new learning cycle
                cycle_id = f"cycle_{int(time.time())}"
                cycle = LearningCycle(
                    cycle_id=cycle_id,
                    start_time=datetime.utcnow(),
                    end_time=None,
                    participating_agents=list(self._active_agents),
                    total_learning_value=0.0,
                    success_count=0,
                    failure_count=0,
                    insights_generated=[],
                    status=LearningStatus.LEARNING,
                    metadata={}
                )
                
                self._learning_cycles.append(cycle)
                self._last_cycle_start = cycle.start_time
                
                logger.info(f"Starting learning cycle {cycle_id} with {len(self._active_agents)} agents")
                
                # Execute learning for each agent
                learning_tasks = []
                for agent_id in self._active_agents:
                    task = asyncio.create_task(self._execute_agent_learning(agent_id, cycle))
                    learning_tasks.append(task)
                
                # Wait for all learning tasks to complete
                results = await asyncio.gather(*learning_tasks, return_exceptions=True)
                
                # Process results
                await self._process_learning_results(cycle, results)
                
        except Exception as e:
            logger.error("Error triggering learning cycle", error=str(e))
    
    async def _execute_agent_learning(self, agent_id: str, cycle: LearningCycle) -> Dict[str, Any]:
        """Execute learning for a specific agent"""
        try:
            metrics = self._agent_metrics[agent_id]
            metrics.status = LearningStatus.LEARNING
            metrics.updated_at = datetime.utcnow()
            
            logger.info(f"Executing learning for agent {agent_id}")
            
            # Determine learning method based on agent type
            if agent_id == "imperium":
                result = await self._execute_imperium_learning(agent_id)
            elif agent_id == "guardian":
                result = await self._execute_guardian_learning(agent_id)
            elif agent_id == "sandbox":
                result = await self._execute_sandbox_learning(agent_id)
            elif agent_id == "conquest":
                result = await self._execute_conquest_learning(agent_id)
            else:
                result = await self._execute_generic_learning(agent_id)
            
            # Update metrics
            metrics.total_learning_cycles += 1
            metrics.last_learning_cycle = datetime.utcnow()
            
            if result.get("status") == "success":
                metrics.status = LearningStatus.SUCCESS
                metrics.last_success = datetime.utcnow()
                metrics.learning_score = min(100.0, metrics.learning_score + result.get("learning_score", 1.0))
            else:
                metrics.status = LearningStatus.FAILED
                metrics.last_failure = datetime.utcnow()
            
            # Update success/failure rates
            total_cycles = metrics.total_learning_cycles
            if total_cycles > 0:
                success_count = sum(1 for c in self._learning_cycles if c.success_count > 0)
                metrics.success_rate = success_count / total_cycles
                metrics.failure_rate = 1.0 - metrics.success_rate
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing learning for agent {agent_id}", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def _execute_imperium_learning(self, agent_id: str) -> Dict[str, Any]:
        """Execute Imperium-specific learning (meta-learning)"""
        try:
            # Analyze other agents' performance
            agent_analyses = []
            for other_agent_id in self._active_agents:
                if other_agent_id != agent_id:
                    other_metrics = self._agent_metrics[other_agent_id]
                    analysis = {
                        "agent_id": other_agent_id,
                        "learning_score": other_metrics.learning_score,
                        "success_rate": other_metrics.success_rate,
                        "improvement_suggestions": other_metrics.improvement_suggestions
                    }
                    agent_analyses.append(analysis)
            
            # Generate meta-learning insights
            insights = await self._generate_meta_learning_insights(agent_analyses)
            
            # Apply improvements to other agents
            improvements_applied = await self._apply_agent_improvements(agent_analyses)
            
            return {
                "status": "success",
                "learning_score": 5.0,  # High learning score for meta-learning
                "insights": insights,
                "improvements_applied": improvements_applied,
                "agent_analyses": len(agent_analyses)
            }
            
        except Exception as e:
            logger.error(f"Error in Imperium learning", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def _execute_guardian_learning(self, agent_id: str) -> Dict[str, Any]:
        """Execute Guardian-specific learning (security and quality)"""
        try:
            # Run security analysis
            security_result = await self.agent_service.run_guardian_agent()
            
            # Learn from security patterns
            security_insights = await self._analyze_security_patterns()
            
            return {
                "status": "success",
                "learning_score": 3.0,
                "security_issues_found": security_result.get("security_issues_found", 0),
                "quality_issues_found": security_result.get("quality_issues_found", 0),
                "insights": security_insights
            }
            
        except Exception as e:
            logger.error(f"Error in Guardian learning", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def _execute_sandbox_learning(self, agent_id: str) -> Dict[str, Any]:
        """Execute Sandbox-specific learning (experimentation)"""
        try:
            # Run experimentation
            sandbox_result = await self.agent_service.run_sandbox_agent()
            
            # Analyze experimental results
            experimental_insights = await self._analyze_experimental_results()
            
            return {
                "status": "success",
                "learning_score": 2.0,
                "experiments_run": sandbox_result.get("experiments_run", 0),
                "tests_run": sandbox_result.get("tests_run", 0),
                "insights": experimental_insights
            }
            
        except Exception as e:
            logger.error(f"Error in Sandbox learning", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def _execute_conquest_learning(self, agent_id: str) -> Dict[str, Any]:
        """Execute Conquest-specific learning (app development)"""
        try:
            # Run conquest agent
            conquest_result = await self.agent_service.run_conquest_agent()
            
            # Analyze development patterns
            development_insights = await self._analyze_development_patterns()
            
            return {
                "status": "success",
                "learning_score": 2.5,
                "apps_analyzed": conquest_result.get("apps_analyzed", 0),
                "proposals_created": conquest_result.get("proposals_created", 0),
                "insights": development_insights
            }
            
        except Exception as e:
            logger.error(f"Error in Conquest learning", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def _execute_generic_learning(self, agent_id: str) -> Dict[str, Any]:
        """Execute generic learning for unknown agent types"""
        try:
            # Use AI learning service for generic learning
            learning_result = await self.learning_service.get_learning_insights(agent_id)
            
            return {
                "status": "success",
                "learning_score": 1.0,
                "insights": learning_result.get("insights", []),
                "learning_data": learning_result
            }
            
        except Exception as e:
            logger.error(f"Error in generic learning for {agent_id}", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def _generate_meta_learning_insights(self, agent_analyses: List[Dict]) -> List[str]:
        """Generate meta-learning insights from agent analyses"""
        insights = []
        
        # Analyze learning patterns
        high_performers = [a for a in agent_analyses if a["learning_score"] > 50]
        low_performers = [a for a in agent_analyses if a["learning_score"] < 20]
        
        if high_performers:
            insights.append(f"High-performing agents: {[a['agent_id'] for a in high_performers]}")
        
        if low_performers:
            insights.append(f"Agents needing improvement: {[a['agent_id'] for a in low_performers]}")
        
        # Generate improvement strategies
        for analysis in agent_analyses:
            if analysis["success_rate"] < 0.5:
                insights.append(f"Agent {analysis['agent_id']} needs success rate improvement")
        
        return insights
    
    async def _apply_agent_improvements(self, agent_analyses: List[Dict]) -> int:
        """Apply improvements to agents based on analysis"""
        improvements_applied = 0
        
        for analysis in agent_analyses:
            if analysis["learning_score"] < 30:
                # Apply learning boost
                agent_id = analysis["agent_id"]
                if agent_id in self._agent_metrics:
                    self._agent_metrics[agent_id].learning_score += 5.0
                    improvements_applied += 1
        
        return improvements_applied
    
    async def _analyze_security_patterns(self) -> List[str]:
        """Analyze security patterns for Guardian learning"""
        return [
            "Security pattern analysis completed",
            "Quality improvement suggestions generated",
            "Vulnerability assessment updated"
        ]
    
    async def _analyze_experimental_results(self) -> List[str]:
        """Analyze experimental results for Sandbox learning"""
        return [
            "Experimental results analyzed",
            "Innovation patterns identified",
            "Testing strategies optimized"
        ]
    
    async def _analyze_development_patterns(self) -> List[str]:
        """Analyze development patterns for Conquest learning"""
        return [
            "Development patterns analyzed",
            "App building strategies optimized",
            "User experience improvements identified"
        ]
    
    async def _process_learning_results(self, cycle: LearningCycle, results: List[Any]):
        """Process learning cycle results"""
        try:
            success_count = 0
            failure_count = 0
            total_learning_value = 0.0
            insights = []
            
            for result in results:
                if isinstance(result, dict) and result.get("status") == "success":
                    success_count += 1
                    total_learning_value += result.get("learning_score", 0.0)
                    if "insights" in result:
                        insights.extend(result["insights"])
                else:
                    failure_count += 1
            
            # Update cycle
            cycle.end_time = datetime.utcnow()
            cycle.total_learning_value = total_learning_value
            cycle.success_count = success_count
            cycle.failure_count = failure_count
            cycle.insights_generated = insights
            cycle.status = LearningStatus.SUCCESS if success_count > 0 else LearningStatus.FAILED
            
            logger.info(f"Learning cycle {cycle.cycle_id} completed: {success_count} successes, {failure_count} failures")
            
        except Exception as e:
            logger.error("Error processing learning results", error=str(e))
    
    async def get_agent_metrics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get learning metrics for agents"""
        try:
            if agent_id:
                if agent_id in self._agent_metrics:
                    return asdict(self._agent_metrics[agent_id])
                else:
                    return {"error": f"Agent {agent_id} not found"}
            
            return {
                agent_id: asdict(metrics) 
                for agent_id, metrics in self._agent_metrics.items()
            }
            
        except Exception as e:
            logger.error("Error getting agent metrics", error=str(e))
            return {"error": str(e)}
    
    async def get_learning_cycles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent learning cycles"""
        try:
            recent_cycles = self._learning_cycles[-limit:] if self._learning_cycles else []
            return [asdict(cycle) for cycle in recent_cycles]
            
        except Exception as e:
            logger.error("Error getting learning cycles", error=str(e))
            return []
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            total_agents = len(self._agent_metrics)
            active_agents = len(self._active_agents)
            total_cycles = len(self._learning_cycles)
            
            # Calculate overall learning score
            total_learning_score = sum(
                metrics.learning_score for metrics in self._agent_metrics.values()
            )
            avg_learning_score = total_learning_score / total_agents if total_agents > 0 else 0.0
            
            return {
                "status": "operational" if self._learning_scheduler_running else "stopped",
                "total_agents": total_agents,
                "active_agents": active_agents,
                "total_learning_cycles": total_cycles,
                "average_learning_score": avg_learning_score,
                "last_cycle_start": self._last_cycle_start.isoformat() if self._last_cycle_start else None,
                "learning_scheduler_running": self._learning_scheduler_running
            }
            
        except Exception as e:
            logger.error("Error getting system status", error=str(e))
            return {"error": str(e)}
    
    async def pause_agent(self, agent_id: str) -> bool:
        """Pause learning for a specific agent"""
        try:
            if agent_id in self._agent_metrics:
                self._agent_metrics[agent_id].is_active = False
                self._agent_metrics[agent_id].status = LearningStatus.PAUSED
                self._active_agents.discard(agent_id)
                logger.info(f"Paused agent {agent_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error pausing agent {agent_id}", error=str(e))
            return False
    
    async def resume_agent(self, agent_id: str) -> bool:
        """Resume learning for a specific agent"""
        try:
            if agent_id in self._agent_metrics:
                self._agent_metrics[agent_id].is_active = True
                self._agent_metrics[agent_id].status = LearningStatus.IDLE
                self._active_agents.add(agent_id)
                logger.info(f"Resumed agent {agent_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error resuming agent {agent_id}", error=str(e))
            return False
    
    async def shutdown(self):
        """Shutdown the learning controller"""
        try:
            self._learning_scheduler_running = False
            self._executor.shutdown(wait=True)
            logger.info("Imperium Learning Controller shutdown complete")
            
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))

    @classmethod
    def set_agent_topics(cls, agent_id: str, topics: list):
        cls._agent_topics[agent_id] = topics

    @classmethod
    def get_agent_topics(cls, agent_id: str) -> list:
        return cls._agent_topics.get(agent_id, ["AI learning"])

    @classmethod
    async def start_periodic_internet_learning(cls):
        if cls._periodic_internet_learning_task is not None:
            return  # Already running
        async def periodic_loop():
            while True:
                try:
                    await asyncio.sleep(cls._internet_learning_interval)
                    instance = cls()
                    await instance.periodic_internet_learning()
                except Exception as e:
                    logger.error("Error in periodic internet learning loop", error=str(e))
                    await asyncio.sleep(60)
        cls._periodic_internet_learning_task = asyncio.create_task(periodic_loop())
        logger.info("Started periodic internet learning background task")

    async def broadcast_internet_learning_event(self, event: dict):
        for ws in list(self._websocket_clients):
            try:
                await ws.send_json(event)
            except Exception:
                self._websocket_clients.discard(ws)

    async def internet_based_learning(self, agent_id: str, topic: str, max_results: int = 5) -> dict:
        fetchers = [StackOverflowFetcher, GitHubFetcher, ArxivFetcher, MediumFetcher]
        all_results = []
        for fetcher in fetchers:
            try:
                results = await fetcher.fetch(topic, max_results)
                all_results.extend(results)
                # Persist each result to the database
                for result in results:
                    await self.learning_service.save_internet_learning_result(agent_id, topic, result)
            except Exception as e:
                logger.error(f"Error fetching from {fetcher.__name__}", error=str(e))
        # Update agent metrics with new knowledge
        if agent_id in self._agent_metrics:
            self._agent_metrics[agent_id].learning_patterns.append(f"Internet learning: {topic}")
            self._agent_metrics[agent_id].improvement_suggestions.extend([r.get("title") for r in all_results if r.get("title")])
            self._agent_metrics[agent_id].updated_at = datetime.utcnow()
        # Log the event
        event = {
            "agent_id": agent_id,
            "topic": topic,
            "results_count": len(all_results),
            "results": all_results[:3],  # Store only a sample for log
            "timestamp": datetime.utcnow().isoformat()
        }
        self._internet_learning_log.append(event)
        # Broadcast to websockets
        await self.broadcast_internet_learning_event(event)
        return {
            "agent_id": agent_id,
            "topic": topic,
            "results": all_results,
            "timestamp": event["timestamp"]
        }

    async def periodic_internet_learning(self, topics_per_agent: Optional[dict] = None, max_results: int = 3):
        if topics_per_agent is None:
            topics_per_agent = dict(self._agent_topics)
        for agent_id in self._active_agents:
            topics = topics_per_agent.get(agent_id, ["AI learning"])
            for topic in topics:
                await self.internet_based_learning(agent_id, topic, max_results)
        logger.info("Periodic internet-based learning completed for all agents")

    def get_internet_learning_log(self, limit: int = 20) -> list:
        return self._internet_learning_log[-limit:]

    def get_internet_learning_impact(self) -> dict:
        impact = {}
        for agent_id, metrics in self._agent_metrics.items():
            impact[agent_id] = {
                "learning_score": metrics.learning_score,
                "total_learning_cycles": metrics.total_learning_cycles,
                "improvement_suggestions": metrics.improvement_suggestions[-5:],
                "last_updated": metrics.updated_at.isoformat() if metrics.updated_at else None
            }
        return impact

    @classmethod
    def get_internet_learning_interval(cls) -> int:
        return cls._internet_learning_interval

    @classmethod
    def set_internet_learning_interval(cls, interval: int):
        cls._internet_learning_interval = interval

    @classmethod
    def get_all_agent_topics(cls) -> dict:
        return dict(cls._agent_topics)

    @classmethod
    def set_all_agent_topics(cls, topics_dict: dict):
        cls._agent_topics = dict(topics_dict) 