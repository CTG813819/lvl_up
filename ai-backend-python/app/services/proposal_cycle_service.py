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

from app.core.database import init_database, SessionLocal
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
    """AI Agent types"""
    IMPERIUM = "imperium"
    GUARDIAN = "guardian"
    SANDBOX = "sandbox"
    CONQUEST = "conquest"

class ProposalCycleService:
    """Manages round-robin proposal generation cycles"""
    
    def __init__(self):
        self.current_agent_index = 0
        self.proposals_per_agent = 5  # Each AI creates 5 proposals before moving to next
        self.agents = [AIAgent.IMPERIUM, AIAgent.GUARDIAN, AIAgent.SANDBOX, AIAgent.CONQUEST]
        self.cycle_status = CycleStatus.ACTIVE
        self.last_cycle_reset = datetime.now()
        self.ai_agent_service = None
        
    @classmethod
    async def initialize(cls):
        """Initialize the proposal cycle service"""
        service = cls()
        service.ai_agent_service = await AIAgentService.initialize()
        logger.info("🔄 Proposal Cycle Service initialized")
        return service
    
    async def get_next_agent(self) -> Optional[AIAgent]:
        """Get the next AI agent that should generate a proposal"""
        try:
            await init_database()
            async with SessionLocal() as session:
                # Check if current cycle is complete (all proposals approved/rejected)
                if await self._is_cycle_complete(session):
                    logger.info("🔄 Cycle complete, starting new cycle")
                    self.current_agent_index = 0
                    self.last_cycle_reset = datetime.now()
                    self.cycle_status = CycleStatus.ACTIVE
                
                # Get current agent
                current_agent = self.agents[self.current_agent_index]
                
                # Check if current agent has completed its quota
                if await self._has_agent_completed_proposals(session, current_agent):
                    # Move to next agent
                    self.current_agent_index = (self.current_agent_index + 1) % len(self.agents)
                    current_agent = self.agents[self.current_agent_index]
                    logger.info(f"🔄 Moving to next agent: {current_agent.value}")
                
                return current_agent
                
        except Exception as e:
            logger.error(f"Error getting next agent: {e}")
            return None
    
    async def _is_cycle_complete(self, session: AsyncSession) -> bool:
        """Check if the current cycle is complete (all proposals approved/rejected)"""
        try:
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
                logger.info("🔄 All proposals processed, cycle complete")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking cycle completion: {e}")
            return False
    
    async def _has_agent_completed_proposals(self, session: AsyncSession, agent: AIAgent) -> bool:
        """Check if an agent has completed its proposal quota"""
        try:
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
            logger.error(f"Error checking agent completion: {e}")
            return False
    
    async def get_cycle_status(self) -> Dict:
        """Get current cycle status"""
        try:
            await init_database()
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
                
                # Get current agent info
                current_agent = self.agents[self.current_agent_index]
                
                return {
                    "cycle_status": self.cycle_status.value,
                    "current_agent": current_agent.value,
                    "agent_index": self.current_agent_index,
                    "proposals_per_agent": self.proposals_per_agent,
                    "last_cycle_reset": self.last_cycle_reset.isoformat(),
                    "proposal_counts": proposal_counts,
                    "total_agents": len(self.agents)
                }
                
        except Exception as e:
            logger.error(f"Error getting cycle status: {e}")
            return {
                "cycle_status": CycleStatus.ERROR.value,
                "error": str(e)
            }
    
    async def force_cycle_reset(self):
        """Force reset the current cycle"""
        try:
            await init_database()
            async with SessionLocal() as session:
                # Delete all proposals
                await session.execute("DELETE FROM proposals")
                await session.commit()
                
                # Reset cycle state
                self.current_agent_index = 0
                self.cycle_status = CycleStatus.ACTIVE
                self.last_cycle_reset = datetime.now()
                
                logger.info("🔄 Cycle force reset completed")
                return {"status": "success", "message": "Cycle reset successfully"}
                
        except Exception as e:
            logger.error(f"Error forcing cycle reset: {e}")
            return {"status": "error", "message": str(e)}
    
    async def get_agent_progress(self, agent: AIAgent) -> Dict:
        """Get progress for a specific agent"""
        try:
            await init_database()
            async with SessionLocal() as session:
                # Count proposals by status for this agent
                query = select(
                    Proposal.status,
                    func.count(Proposal.id).label('count')
                ).where(
                    Proposal.ai_type == agent.value
                ).group_by(Proposal.status)
                
                result = await session.execute(query)
                status_counts = {}
                
                for row in result:
                    status_counts[row.status] = row.count
                
                pending_count = status_counts.get("pending", 0)
                progress = min(pending_count / self.proposals_per_agent, 1.0)
                
                return {
                    "agent": agent.value,
                    "pending_count": pending_count,
                    "quota": self.proposals_per_agent,
                    "progress": progress,
                    "is_complete": pending_count >= self.proposals_per_agent,
                    "status_counts": status_counts
                }
                
        except Exception as e:
            logger.error(f"Error getting agent progress: {e}")
            return {"error": str(e)} 