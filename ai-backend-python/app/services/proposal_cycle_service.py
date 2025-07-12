"""
Proposal Cycle Service
Manages round-robin proposal generation cycles for AI agents
"""

import asyncio
import structlog
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import init_database
from app.models.sql_models import Proposal
from app.services.ai_agent_service import AIAgentService

logger = structlog.get_logger()

class CycleStatus(Enum):
    """Status of a proposal cycle"""
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ERROR = "error"

class AIAgent(Enum):
    """AI agents in the cycle"""
    IMPERIUM = "imperium"
    GUARDIAN = "guardian"
    SANDBOX = "sandbox"
    CONQUEST = "conquest"

class ProposalCycleService:
    """
    Manages round-robin proposal generation cycles
    
    Cycle Logic:
    1. Each AI creates 5 proposals before moving to next AI
    2. Cycle continues until all proposals are approved/rejected
    3. New cycle begins when all proposals are resolved
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ProposalCycleService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ai_agent_service = AIAgentService()
            self.current_cycle = 1
            self.current_agent_index = 0
            self.agents = [AIAgent.IMPERIUM, AIAgent.GUARDIAN, AIAgent.SANDBOX, AIAgent.CONQUEST]
            self.proposals_per_agent = 5
            self.cycle_status = CycleStatus.PAUSED
            self.last_cycle_check = None
            self.cycle_check_interval = 60  # seconds
            self._running = False
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the proposal cycle service"""
        instance = cls()
        await instance.ai_agent_service.initialize()
        logger.info("Proposal Cycle Service initialized")
        return instance
    
    async def start_cycle_service(self):
        """Start the proposal cycle service"""
        if self._running:
            logger.warning("Proposal cycle service already running")
            return
        
        self._running = True
        self.cycle_status = CycleStatus.ACTIVE
        logger.info("🔄 Starting proposal cycle service")
        
        try:
            while self._running:
                await self._run_cycle_check()
                await asyncio.sleep(self.cycle_check_interval)
        except asyncio.CancelledError:
            logger.info("Proposal cycle service cancelled")
        except Exception as e:
            logger.error("Error in proposal cycle service", error=str(e))
            self.cycle_status = CycleStatus.ERROR
        finally:
            self._running = False
    
    async def stop_cycle_service(self):
        """Stop the proposal cycle service"""
        self._running = False
        self.cycle_status = CycleStatus.PAUSED
        logger.info("🔄 Stopping proposal cycle service")
    
    async def _run_cycle_check(self):
        """Run a cycle check and generate proposals if needed"""
        try:
            # Check if current cycle is complete
            if await self._is_cycle_complete():
                await self._start_new_cycle()
                return
            
            # Check if current agent has completed its proposals
            current_agent = self.agents[self.current_agent_index]
            if await self._has_agent_completed_proposals(current_agent):
                await self._move_to_next_agent()
                return
            
            # Generate proposal for current agent
            await self._generate_proposal_for_agent(current_agent)
            
        except Exception as e:
            logger.error("Error in cycle check", error=str(e))
            self.cycle_status = CycleStatus.ERROR
    
    async def _is_cycle_complete(self) -> bool:
        """Check if the current cycle is complete (all proposals approved/rejected)"""
        try:
            from app.core.database import SessionLocal
            
            async with SessionLocal() as session:
                # Count pending proposals
                pending_query = select(func.count(Proposal.id)).where(Proposal.status == "pending")
                pending_result = await session.execute(pending_query)
                pending_count = pending_result.scalar() or 0
                
                # Count in_review proposals
                review_query = select(func.count(Proposal.id)).where(Proposal.status == "in_review")
                review_result = await session.execute(review_query)
                review_count = review_result.scalar() or 0
                
                total_active = pending_count + review_count
                
                if total_active == 0:
                    logger.info("🔄 Cycle complete - no active proposals")
                    return True
                
                return False
                
        except Exception as e:
            logger.error("Error checking cycle completion", error=str(e))
            return False
    
    async def _start_new_cycle(self):
        """Start a new proposal cycle"""
        try:
            self.current_cycle += 1
            self.current_agent_index = 0
            self.cycle_status = CycleStatus.ACTIVE
            
            logger.info(f"🔄 Starting new proposal cycle {self.current_cycle}")
            logger.info(f"🔄 First agent: {self.agents[self.current_agent_index].value}")
            
            # Generate first proposal for the new cycle
            first_agent = self.agents[self.current_agent_index]
            await self._generate_proposal_for_agent(first_agent)
            
        except Exception as e:
            logger.error("Error starting new cycle", error=str(e))
            self.cycle_status = CycleStatus.ERROR
    
    async def _has_agent_completed_proposals(self, agent: AIAgent) -> bool:
        """Check if an agent has completed its proposal quota"""
        try:
            from app.core.database import SessionLocal
            
            async with SessionLocal() as session:
                # Count pending proposals for this agent
                query = select(func.count(Proposal.id)).where(
                    Proposal.status == "pending",
                    Proposal.ai_type == agent.value
                )
                result = await session.execute(query)
                pending_count = result.scalar() or 0
                
                # Check if agent has reached its quota
                if pending_count >= self.proposals_per_agent:
                    logger.info(f"🔄 Agent {agent.value} has completed {pending_count} proposals")
                    return True
                
                return False
                
        except Exception as e:
            logger.error(f"Error checking agent completion for {agent.value}", error=str(e))
            return False
    
    async def _move_to_next_agent(self):
        """Move to the next agent in the cycle"""
        try:
            self.current_agent_index = (self.current_agent_index + 1) % len(self.agents)
            next_agent = self.agents[self.current_agent_index]
            
            logger.info(f"🔄 Moving to next agent: {next_agent.value}")
            
            # Generate first proposal for the new agent
            await self._generate_proposal_for_agent(next_agent)
            
        except Exception as e:
            logger.error("Error moving to next agent", error=str(e))
            self.cycle_status = CycleStatus.ERROR
    
    async def _generate_proposal_for_agent(self, agent: AIAgent):
        """Generate a proposal for the specified agent"""
        try:
            logger.info(f"🔄 Generating proposal for {agent.value}")
            
            # Check if agent already has enough pending proposals
            if await self._has_agent_completed_proposals(agent):
                logger.info(f"🔄 Agent {agent.value} already has enough proposals")
                return
            
            # Generate proposal based on agent type
            if agent == AIAgent.IMPERIUM:
                result = await self.ai_agent_service.run_imperium_agent()
            elif agent == AIAgent.GUARDIAN:
                result = await self.ai_agent_service.run_guardian_agent()
            elif agent == AIAgent.SANDBOX:
                result = await self.ai_agent_service.run_sandbox_agent()
            elif agent == AIAgent.CONQUEST:
                result = await self.ai_agent_service.run_conquest_agent()
            else:
                logger.error(f"Unknown agent type: {agent}")
                return
            
            if result and result.get("status") == "success":
                logger.info(f"✅ Generated proposal for {agent.value}")
            else:
                logger.warning(f"⚠️ Failed to generate proposal for {agent.value}: {result}")
            
        except Exception as e:
            logger.error(f"Error generating proposal for {agent.value}", error=str(e))
    
    async def get_cycle_status(self) -> Dict:
        """Get current cycle status"""
        try:
            from app.core.database import SessionLocal
            
            async with SessionLocal() as session:
                # Get proposal counts by status and agent
                status_query = select(
                    Proposal.ai_type,
                    Proposal.status,
                    func.count(Proposal.id).label('count')
                ).group_by(Proposal.ai_type, Proposal.status)
                
                result = await session.execute(status_query)
                proposal_counts = {}
                
                for row in result:
                    ai_type = row.ai_type
                    status = row.status
                    count = row.count
                    
                    if ai_type not in proposal_counts:
                        proposal_counts[ai_type] = {}
                    
                    proposal_counts[ai_type][status] = count
                
                return {
                    "cycle_number": self.current_cycle,
                    "current_agent": self.agents[self.current_agent_index].value,
                    "cycle_status": self.cycle_status.value,
                    "proposals_per_agent": self.proposals_per_agent,
                    "proposal_counts": proposal_counts,
                    "service_running": self._running
                }
                
        except Exception as e:
            logger.error("Error getting cycle status", error=str(e))
            return {
                "error": str(e),
                "cycle_status": self.cycle_status.value,
                "service_running": self._running
            }
    
    async def force_new_cycle(self):
        """Force start a new cycle (for testing/debugging)"""
        try:
            logger.info("🔄 Forcing new cycle")
            await self._start_new_cycle()
        except Exception as e:
            logger.error("Error forcing new cycle", error=str(e))
    
    async def reset_cycle(self):
        """Reset the cycle to start from the beginning"""
        try:
            logger.info("🔄 Resetting cycle")
            self.current_cycle = 1
            self.current_agent_index = 0
            self.cycle_status = CycleStatus.ACTIVE
        except Exception as e:
            logger.error("Error resetting cycle", error=str(e)) 