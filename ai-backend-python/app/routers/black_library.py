"""
Black Library Router
API endpoints for the Black Library screen
Provides learning data and custody data for AI visualization
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.sql_models import Proposal, Learning, AgentMetrics, Experiment
from app.services.ai_learning_service import AILearningService
from app.services.ai_growth_service import AIGrowthService
from app.services.custody_protocol_service import CustodyProtocolService

logger = structlog.get_logger()
router = APIRouter(prefix="/api/black-library", tags=["Black Library"])


@router.get("/live-data")
async def get_black_library_live_data(session: AsyncSession = Depends(get_db)):
    """Get comprehensive Black Library data including learning trees and custody results"""
    try:
        # Initialize services
        ai_learning_service = AILearningService()
        ai_growth_service = AIGrowthService()
        custody_service = await CustodyProtocolService.initialize()
        
        # Get custody analytics
        custody_analytics = await custody_service.get_custody_analytics()
        
        # Get AI data for each agent type
        ai_types = ["imperium", "guardian", "sandbox", "conquest"]
        ai_data = {}
        total_learning_score = 0.0
        total_xp = 0
        
        # Get growth insights from the growth service
        growth_insights = await ai_growth_service.get_growth_insights()
        ai_growth_data = growth_insights.get('ai_growth_insights', {})
        
        for ai_type in ai_types:
            # Get learning score from growth insights
            ai_growth = ai_growth_data.get(ai_type.title(), {})
            learning_score = ai_growth.get('growth_score', 0.0)
            ai_level = 1  # Default level
            level_progress = learning_score / 100.0  # Progress as percentage of 100

            # Get custody metrics for this AI
            custody_metrics = custody_analytics.get("ai_specific_metrics", {}).get(ai_type, {})

            # Get recent learning data as nodes
            learning_nodes = []
            learning_query = await session.execute(
                select(Learning).where(Learning.ai_type == ai_type).order_by(Learning.created_at.desc()).limit(50)
            )
            for learning in learning_query.scalars().all():
                learning_nodes.append({
                    'id': str(learning.id),
                    'learning_type': learning.learning_type,
                    'learning_data': learning.learning_data,
                    'created_at': learning.created_at.isoformat() if learning.created_at else None,
                    'status': learning.status
                })

            # PATCH: If no learning_nodes, fallback to learning_patterns from custody_metrics
            if not learning_nodes and 'learning_patterns' in custody_metrics:
                patterns = custody_metrics['learning_patterns']
                learning_nodes = [
                    {
                        'id': f"{ai_type}_pattern_{idx}",
                        'learning_type': pattern.split(':')[0] if ':' in pattern else 'pattern',
                        'learning_data': pattern,
                        'created_at': None,
                        'status': 'active'
                    }
                    for idx, pattern in enumerate(patterns)
                ]

            # FURTHER PATCH: If still no learning_nodes, try AgentMetrics table
            if not learning_nodes:
                agent_metrics_query = await session.execute(
                    select(AgentMetrics).where(AgentMetrics.agent_type == ai_type)
                )
                agent_metrics_row = agent_metrics_query.scalars().first()
                if agent_metrics_row and getattr(agent_metrics_row, 'learning_patterns', None):
                    patterns = agent_metrics_row.learning_patterns
                    learning_nodes = [
                        {
                            'id': f"{ai_type}_pattern_{idx}",
                            'learning_type': pattern.split(':')[0] if ':' in pattern else 'pattern',
                            'learning_data': pattern,
                            'created_at': None,
                            'status': 'active'
                        }
                        for idx, pattern in enumerate(patterns)
                    ]

            ai_data[ai_type] = {
                'level': ai_level,
                'title': _get_agent_level_and_title(learning_score, ai_type),
                'knowledge_points': int(learning_score * 0.1),
                'xp': int(learning_score),
                'custody_xp': custody_metrics.get('custody_xp', 0),
                'level_progress': level_progress,
                'learning_score': learning_score,
                'last_activity': datetime.utcnow().isoformat(),
                'learning_nodes': learning_nodes,
                'custodes_status': {
                    'last_test': custody_metrics.get('last_test_date'),
                    'test_status': 'active' if custody_metrics.get('total_tests_given', 0) > 0 else 'inactive',
                    'pass_rate': custody_metrics.get('pass_rate', 0.0),
                    'total_tests': custody_metrics.get('total_tests_given', 0),
                    'eligible_for_proposals': custody_metrics.get('can_create_proposals', False)
                },
                'autonomous_learning': {
                    'last_learning_cycle': await _get_last_learning_cycle(session, ai_type),
                    'subjects_learned': _get_subjects_learned(ai_type),
                    'internet_learning_active': True,
                    'cross_ai_learning': True,
                    'learning_cycle_status': 'active'
                },
                'recent_learnings': await _get_recent_learning_data(session, ai_type)
            }
            
            total_learning_score += learning_score
            total_xp += int(learning_score)
        
        return {
            "status": "success",
            "ai_data": ai_data,
            "unified_leveling": {
                "total_learning_score": total_learning_score,
                "total_xp": total_xp,
                "system_status": "online"
            },
            "total_learning_score": total_learning_score,
            "total_xp": total_xp,
            "last_updated": datetime.utcnow().isoformat(),
            "system_status": "online"
        }
        
    except Exception as e:
        logger.error("Error getting Black Library live data", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/learning-tree/{ai_type}")
async def get_ai_learning_tree(ai_type: str, session: AsyncSession = Depends(get_db)):
    """Get detailed learning tree for a specific AI"""
    try:
        if ai_type not in ["imperium", "guardian", "sandbox", "conquest"]:
            raise HTTPException(status_code=400, detail=f"Invalid AI type: {ai_type}")
        
        # Get learning score
        ai_growth_service = AIGrowthService()
        learning_score = await ai_growth_service.get_growth_score(ai_type) or 0.0
        
        # Generate learning tree
        learning_tree = _generate_learning_tree(ai_type, learning_score)
        
        return {
            "status": "success",
            "ai_type": ai_type,
            "learning_score": learning_score,
            "learning_tree": learning_tree,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting learning tree for {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/custody-results/{ai_type}")
async def get_ai_custody_results(ai_type: str, session: AsyncSession = Depends(get_db)):
    """Get custody test results for a specific AI"""
    try:
        if ai_type not in ["imperium", "guardian", "sandbox", "conquest"]:
            raise HTTPException(status_code=400, detail=f"Invalid AI type: {ai_type}")
        
        # Get custody analytics
        custody_service = await CustodyProtocolService.initialize()
        custody_analytics = await custody_service.get_custody_analytics()
        
        ai_metrics = custody_analytics.get("ai_specific_metrics", {}).get(ai_type, {})
        
        return {
            "status": "success",
            "ai_type": ai_type,
            "custody_metrics": ai_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting custody results for {ai_type}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


async def _get_recent_learning_data(session: AsyncSession, ai_type: str) -> List[str]:
    """Get recent learning data for an AI"""
    try:
        # Get recent proposals for this AI
        proposals_result = await session.execute(
            select(Proposal)
            .where(Proposal.ai_type == ai_type.title())
            .order_by(Proposal.created_at.desc())
            .limit(5)
        )
        proposals = proposals_result.scalars().all()
        
        # Get recent experiments for this AI
        experiments_result = await session.execute(
            select(Experiment)
            .where(Experiment.ai_type == ai_type.title())
            .order_by(Experiment.created_at.desc())
            .limit(5)
        )
        experiments = experiments_result.scalars().all()
        
        learnings = []
        
        # Add learnings from proposals
        for proposal in proposals:
            if proposal.status == "approved":
                learnings.append(f"Successfully implemented {proposal.improvement_type or 'improvement'}")
            elif proposal.status == "rejected":
                learnings.append(f"Learned from rejection: {proposal.user_feedback_reason or 'improvement needed'}")
        
        # Add learnings from experiments
        for experiment in experiments:
            if experiment.status == "passed":
                learnings.append(f"Experiment successful: {experiment.description or 'test completed'}")
            elif experiment.status == "failed":
                learnings.append(f"Experiment failed: {experiment.description or 'test failed'}")
        
        # Add AI-specific learnings
        ai_specific_learnings = {
            "imperium": [
                "Enhanced system architecture understanding",
                "Improved oversight and coordination",
                "Strengthened decision-making frameworks"
            ],
            "guardian": [
                "Strengthened security protocols",
                "Enhanced quality assurance processes",
                "Improved threat detection capabilities"
            ],
            "sandbox": [
                "Explored experimental AI capabilities",
                "Tested innovative approaches",
                "Developed creative solutions"
            ],
            "conquest": [
                "Optimized code generation algorithms",
                "Enhanced performance optimization",
                "Improved code quality analysis"
            ]
        }
        
        learnings.extend(ai_specific_learnings.get(ai_type, []))
        
        return learnings[:5]  # Limit to 5 most recent
        
    except Exception as e:
        logger.error(f"Error getting recent learning data for {ai_type}", error=str(e))
        return []


def _generate_learning_tree(ai_type: str, learning_score: float) -> Dict[str, Any]:
    """Generate learning tree for an AI based on their learning score"""
    
    # Define learning trees for each AI type
    learning_trees = {
        "imperium": {
            "nodes": [
                {"id": "system_architecture", "name": "System Architecture", "unlocked": learning_score >= 100, "custodes_verified": True},
                {"id": "code_optimization", "name": "Code Optimization", "unlocked": learning_score >= 300, "custodes_verified": True},
                {"id": "security_patterns", "name": "Security Patterns", "unlocked": learning_score >= 600, "custodes_verified": True},
                {"id": "ai_coordination", "name": "AI Coordination", "unlocked": learning_score >= 1000, "custodes_verified": True},
                {"id": "system_governance", "name": "System Governance", "unlocked": learning_score >= 1500, "custodes_verified": True},
                {"id": "autonomous_learning", "name": "Autonomous Learning", "unlocked": learning_score >= 2000, "custodes_verified": True},
                {"id": "internet_knowledge", "name": "Internet Knowledge", "unlocked": learning_score >= 2500, "custodes_verified": True}
            ],
            "connections": [
                {"from": "system_architecture", "to": "code_optimization"},
                {"from": "code_optimization", "to": "security_patterns"},
                {"from": "security_patterns", "to": "ai_coordination"},
                {"from": "ai_coordination", "to": "system_governance"},
                {"from": "system_governance", "to": "autonomous_learning"},
                {"from": "autonomous_learning", "to": "internet_knowledge"}
            ]
        },
        "guardian": {
            "nodes": [
                {"id": "security_basics", "name": "Security Basics", "unlocked": learning_score >= 100, "custodes_verified": True},
                {"id": "threat_detection", "name": "Threat Detection", "unlocked": learning_score >= 300, "custodes_verified": True},
                {"id": "code_review", "name": "Code Review", "unlocked": learning_score >= 600, "custodes_verified": True},
                {"id": "vulnerability_assessment", "name": "Vulnerability Assessment", "unlocked": learning_score >= 1000, "custodes_verified": True},
                {"id": "security_governance", "name": "Security Governance", "unlocked": learning_score >= 1500, "custodes_verified": True},
                {"id": "penetration_testing", "name": "Penetration Testing", "unlocked": learning_score >= 2000, "custodes_verified": True},
                {"id": "ethical_hacking", "name": "Ethical Hacking", "unlocked": learning_score >= 2500, "custodes_verified": True}
            ],
            "connections": [
                {"from": "security_basics", "to": "threat_detection"},
                {"from": "threat_detection", "to": "code_review"},
                {"from": "code_review", "to": "vulnerability_assessment"},
                {"from": "vulnerability_assessment", "to": "security_governance"},
                {"from": "security_governance", "to": "penetration_testing"},
                {"from": "penetration_testing", "to": "ethical_hacking"}
            ]
        },
        "sandbox": {
            "nodes": [
                {"id": "experimentation", "name": "Experimentation", "unlocked": learning_score >= 100, "custodes_verified": True},
                {"id": "innovation_patterns", "name": "Innovation Patterns", "unlocked": learning_score >= 300, "custodes_verified": True},
                {"id": "prototype_development", "name": "Prototype Development", "unlocked": learning_score >= 600, "custodes_verified": True},
                {"id": "advanced_testing", "name": "Advanced Testing", "unlocked": learning_score >= 1000, "custodes_verified": True},
                {"id": "research_methodology", "name": "Research Methodology", "unlocked": learning_score >= 1500, "custodes_verified": True},
                {"id": "experimental_ai", "name": "Experimental AI", "unlocked": learning_score >= 2000, "custodes_verified": True},
                {"id": "creative_problem_solving", "name": "Creative Problem Solving", "unlocked": learning_score >= 2500, "custodes_verified": True}
            ],
            "connections": [
                {"from": "experimentation", "to": "innovation_patterns"},
                {"from": "innovation_patterns", "to": "prototype_development"},
                {"from": "prototype_development", "to": "advanced_testing"},
                {"from": "advanced_testing", "to": "research_methodology"},
                {"from": "research_methodology", "to": "experimental_ai"},
                {"from": "experimental_ai", "to": "creative_problem_solving"}
            ]
        },
        "conquest": {
            "nodes": [
                {"id": "code_generation", "name": "Code Generation", "unlocked": learning_score >= 100, "custodes_verified": True},
                {"id": "optimization_techniques", "name": "Optimization Techniques", "unlocked": learning_score >= 300, "custodes_verified": True},
                {"id": "performance_analysis", "name": "Performance Analysis", "unlocked": learning_score >= 600, "custodes_verified": True},
                {"id": "scalability_patterns", "name": "Scalability Patterns", "unlocked": learning_score >= 1000, "custodes_verified": True},
                {"id": "advanced_automation", "name": "Advanced Automation", "unlocked": learning_score >= 1500, "custodes_verified": True},
                {"id": "app_development", "name": "App Development", "unlocked": learning_score >= 2000, "custodes_verified": True},
                {"id": "user_experience", "name": "User Experience", "unlocked": learning_score >= 2500, "custodes_verified": True}
            ],
            "connections": [
                {"from": "code_generation", "to": "optimization_techniques"},
                {"from": "optimization_techniques", "to": "performance_analysis"},
                {"from": "performance_analysis", "to": "scalability_patterns"},
                {"from": "scalability_patterns", "to": "advanced_automation"},
                {"from": "advanced_automation", "to": "app_development"},
                {"from": "app_development", "to": "user_experience"}
            ]
        }
    }
    
    return learning_trees.get(ai_type, {"nodes": [], "connections": []})


def _get_agent_level_and_title(learning_score: float, ai_type: str) -> str:
    """Get agent level and title based on learning score and AI type"""
    
    # Unified leveling system
    if learning_score >= 2000000:
        if ai_type == "imperium":
            return "Emperor"
        elif ai_type == "guardian":
            return "Chapter Master"
        elif ai_type == "conquest":
            return "Fabricator General"
        elif ai_type == "sandbox":
            return "Fabricator General"
    elif learning_score >= 1000000:
        return "Master of the Forge"
    elif learning_score >= 500000:
        if ai_type == "imperium":
            return "Librarian"
        elif ai_type == "guardian":
            return "Techmarine"
        elif ai_type == "conquest":
            return "Archmagos"
        elif ai_type == "sandbox":
            return "Archmagos"
    elif learning_score >= 200000:
        if ai_type == "conquest":
            return "Tech Priest Dominus"
        elif ai_type == "sandbox":
            return "Tech Priest Dominus"
        else:
            return "Lieutenant"
    elif learning_score >= 100000:
        if ai_type == "conquest":
            return "Magos"
        elif ai_type == "sandbox":
            return "Magos"
        else:
            return "Sergeant"
    elif learning_score >= 50000:
        if ai_type == "conquest":
            return "Tech Priest (Engineer)"
        elif ai_type == "sandbox":
            return "Tech Priest (Cogitator)"
        else:
            return "Veteran"
    elif learning_score >= 20000:
        if ai_type == "conquest":
            return "Initiate/Apprentice"
        elif ai_type == "sandbox":
            return "Initiate/Apprentice"
        else:
            return "Battle Brother"
    elif learning_score >= 10000:
        if ai_type == "conquest":
            return "Skitarii"
        elif ai_type == "sandbox":
            return "Skitarii"
        else:
            return "Neophyte"
    elif learning_score >= 5000:
        if ai_type == "conquest":
            return "Servitor"
        elif ai_type == "sandbox":
            return "Servitor"
        else:
            return "Aspirant"
    elif learning_score >= 2000:
        if ai_type == "conquest":
            return "Menial"
        elif ai_type == "sandbox":
            return "Menial"
        else:
            return "Recruit"
    else:
        if ai_type == "conquest":
            return "Cadet"
        elif ai_type == "sandbox":
            return "Cadet"
        else:
            return "Recruit"
    
    return "Recruit"


async def _get_last_learning_cycle(session: AsyncSession, ai_type: str) -> str:
    """Get the last learning cycle timestamp for an AI"""
    try:
        # Get the most recent proposal or experiment for this AI
        latest_proposal_result = await session.execute(
            select(Proposal)
            .where(Proposal.ai_type == ai_type.title())
            .order_by(Proposal.created_at.desc())
            .limit(1)
        )
        latest_proposal = latest_proposal_result.scalar_one_or_none()
        
        latest_experiment_result = await session.execute(
            select(Experiment)
            .where(Experiment.ai_type == ai_type.title())
            .order_by(Experiment.created_at.desc())
            .limit(1)
        )
        latest_experiment = latest_experiment_result.scalar_one_or_none()
        
        # Return the most recent timestamp
        if latest_proposal and latest_experiment:
            if latest_proposal.created_at > latest_experiment.created_at:
                return latest_proposal.created_at.isoformat()
            else:
                return latest_experiment.created_at.isoformat()
        elif latest_proposal:
            return latest_proposal.created_at.isoformat()
        elif latest_experiment:
            return latest_experiment.created_at.isoformat()
        else:
            return (datetime.utcnow() - timedelta(hours=1)).isoformat()
            
    except Exception as e:
        logger.error(f"Error getting last learning cycle for {ai_type}", error=str(e))
        return (datetime.utcnow() - timedelta(hours=1)).isoformat()


def _get_subjects_learned(ai_type: str) -> List[str]:
    """Get subjects learned by an AI"""
    # This would ideally query the learning database
    # For now, return AI-specific subjects
    subjects = {
        "imperium": ["system_architecture", "ai_governance", "coordination"],
        "guardian": ["security", "code_quality", "threat_detection"],
        "sandbox": ["experimentation", "innovation", "research"],
        "conquest": ["code_generation", "optimization", "app_development"]
    }
    
    return subjects.get(ai_type, ["general_learning"]) 