"""
Agent Metrics Router
Provides API endpoints for agent metrics operations
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from datetime import datetime
import structlog

from ..services.agent_metrics_service import AgentMetricsService

logger = structlog.get_logger()
router = APIRouter()


@router.get("/leaderboard")
async def get_leaderboard():
    """Get leaderboard with all agent metrics including custody XP and win rate"""
    try:
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        
        # Get all agent metrics
        all_metrics = await agent_metrics_service.get_all_agent_metrics()
        
        # Convert to leaderboard format
        leaderboard = []
        for ai_type, metrics in all_metrics.items():
            # Calculate win rate from adversarial wins and total tests
            total_tests = metrics.get('total_tests_given', 0)
            adversarial_wins = metrics.get('adversarial_wins', 0)
            win_rate = (adversarial_wins / total_tests) if total_tests > 0 else 0.0
            
            # Get recent score from test history
            test_history = metrics.get('test_history', [])
            recent_score = 0
            if test_history:
                recent_score = test_history[-1].get('score', 0) if isinstance(test_history[-1], dict) else 0
            
            leaderboard_entry = {
                'ai_type': ai_type,
                'level': metrics.get('level', 1),
                'learning_score': metrics.get('learning_score', 0.0),
                'custody_xp': metrics.get('custody_xp', 0),
                'win_rate': win_rate,
                'recent_score': recent_score,
                'total_tests': total_tests,
                'adversarial_wins': adversarial_wins,
                'pass_rate': metrics.get('pass_rate', 0.0),
                'xp': metrics.get('xp', 0),
                'consecutive_successes': metrics.get('consecutive_successes', 0),
                'consecutive_failures': metrics.get('consecutive_failures', 0),
                'last_test_date': metrics.get('last_test_date'),
                'status': metrics.get('status', 'active')
            }
            leaderboard.append(leaderboard_entry)
        
        # Sort by learning score, then custody XP, then win rate
        leaderboard.sort(key=lambda x: (
            x['learning_score'], 
            x['custody_xp'], 
            x['win_rate']
        ), reverse=True)
        
        return {
            "status": "success",
            "leaderboard": leaderboard,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting leaderboard: {str(e)}")


@router.get("/metrics/{agent_type}")
async def get_agent_metrics(agent_type: str):
    """Get metrics for a specific agent"""
    try:
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        
        metrics = await agent_metrics_service.get_agent_metrics(agent_type)
        
        if not metrics:
            raise HTTPException(status_code=404, detail=f"Agent {agent_type} not found")
        
        return {
            "status": "success",
            "agent_type": agent_type,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics for {agent_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting metrics: {str(e)}")


@router.get("/all")
async def get_all_metrics():
    """Get metrics for all agents"""
    try:
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        
        all_metrics = await agent_metrics_service.get_all_agent_metrics()
        
        return {
            "status": "success",
            "metrics": all_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting all metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting all metrics: {str(e)}")


@router.post("/update/{agent_type}")
async def update_agent_metrics(agent_type: str, updates: Dict[str, Any]):
    """Update metrics for a specific agent"""
    try:
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        
        success = await agent_metrics_service.update_specific_metrics(agent_type, updates)
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to update metrics for {agent_type}")
        
        return {
            "status": "success",
            "message": f"Metrics updated for {agent_type}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating metrics for {agent_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating metrics: {str(e)}")


@router.post("/reset/{agent_type}")
async def reset_agent_metrics(agent_type: str):
    """Reset metrics for a specific agent"""
    try:
        agent_metrics_service = AgentMetricsService()
        await agent_metrics_service.initialize()
        
        success = await agent_metrics_service.reset_agent_metrics(agent_type)
        
        if not success:
            raise HTTPException(status_code=500, detail=f"Failed to reset metrics for {agent_type}")
        
        return {
            "status": "success",
            "message": f"Metrics reset for {agent_type}",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting metrics for {agent_type}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error resetting metrics: {str(e)}") 