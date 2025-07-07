"""
Imperium Learning Controller API Router
Provides REST endpoints for the master learning orchestrator
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket, WebSocketDisconnect, Body
from typing import Dict, List, Optional, Any
import structlog
from datetime import datetime

from ..services.imperium_learning_controller import ImperiumLearningController
from ..core.database import get_session
from ..services import trusted_sources

logger = structlog.get_logger()

router = APIRouter(prefix="/api/imperium", tags=["Imperium Learning Controller"])

# Global instance of the learning controller
_learning_controller: Optional[ImperiumLearningController] = None


async def get_learning_controller() -> ImperiumLearningController:
    """Get or initialize the learning controller instance"""
    global _learning_controller
    if _learning_controller is None:
        _learning_controller = await ImperiumLearningController.initialize()
    return _learning_controller


@router.post("/initialize")
async def initialize_imperium_learning_controller(
    background_tasks: BackgroundTasks,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Initialize the Imperium Learning Controller"""
    try:
        logger.info("Initializing Imperium Learning Controller via API")
        
        # The controller is already initialized in get_learning_controller
        # This endpoint provides a way to trigger re-initialization if needed
        
        return {
            "status": "success",
            "message": "Imperium Learning Controller initialized successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error initializing Imperium Learning Controller", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_system_status(
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Get overall system status"""
    try:
        status = await controller.get_system_status()
        return status
        
    except Exception as e:
        logger.error("Error getting system status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def get_all_agents(
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Get all registered agents and their metrics"""
    try:
        metrics = await controller.get_agent_metrics()
        return {
            "agents": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting agent metrics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/{agent_id}")
async def get_agent_metrics(
    agent_id: str,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Get metrics for a specific agent"""
    try:
        metrics = await controller.get_agent_metrics(agent_id)
        
        if "error" in metrics:
            raise HTTPException(status_code=404, detail=metrics["error"])
        
        return {
            "agent": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting metrics for agent {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/register")
async def register_agent(
    agent_data: Dict[str, Any],
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Register a new AI agent"""
    try:
        agent_id = agent_data.get("agent_id")
        agent_type = agent_data.get("agent_type")
        priority = agent_data.get("priority", "medium")
        
        if not agent_id or not agent_type:
            raise HTTPException(status_code=400, detail="agent_id and agent_type are required")
        
        success = await controller.register_agent(agent_id, agent_type, priority)
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to register agent")
        
        return {
            "status": "success",
            "message": f"Agent {agent_id} registered successfully",
            "agent_id": agent_id,
            "agent_type": agent_type,
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error registering agent", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agents/{agent_id}")
async def unregister_agent(
    agent_id: str,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Unregister an AI agent"""
    try:
        success = await controller.unregister_agent(agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return {
            "status": "success",
            "message": f"Agent {agent_id} unregistered successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unregistering agent {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/pause")
async def pause_agent(
    agent_id: str,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Pause learning for a specific agent"""
    try:
        success = await controller.pause_agent(agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return {
            "status": "success",
            "message": f"Agent {agent_id} paused successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing agent {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agents/{agent_id}/resume")
async def resume_agent(
    agent_id: str,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Resume learning for a specific agent"""
    try:
        success = await controller.resume_agent(agent_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        
        return {
            "status": "success",
            "message": f"Agent {agent_id} resumed successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming agent {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cycles")
async def get_learning_cycles(
    limit: int = 10,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Get recent learning cycles"""
    try:
        cycles = await controller.get_learning_cycles(limit)
        return {
            "cycles": cycles,
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting learning cycles", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cycles/trigger")
async def trigger_learning_cycle(
    background_tasks: BackgroundTasks,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Manually trigger a learning cycle"""
    try:
        logger.info("Manually triggering learning cycle via API")
        
        # Trigger the learning cycle in the background
        background_tasks.add_task(controller._trigger_learning_cycle)
        
        return {
            "status": "success",
            "message": "Learning cycle triggered successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error triggering learning cycle", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_learning_dashboard(
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Get comprehensive learning dashboard data"""
    try:
        # Get all the data for the dashboard
        system_status = await controller.get_system_status()
        agent_metrics = await controller.get_agent_metrics()
        recent_cycles = await controller.get_learning_cycles(5)
        
        # Calculate additional metrics
        total_learning_score = sum(
            metrics.get("learning_score", 0) 
            for metrics in agent_metrics.values() 
            if isinstance(metrics, dict)
        )
        
        active_agents = sum(
            1 for metrics in agent_metrics.values() 
            if isinstance(metrics, dict) and metrics.get("is_active", False)
        )
        
        return {
            "system_status": system_status,
            "agent_metrics": agent_metrics,
            "recent_cycles": recent_cycles,
            "dashboard_metrics": {
                "total_learning_score": total_learning_score,
                "active_agents": active_agents,
                "total_agents": len(agent_metrics),
                "recent_cycles_count": len(recent_cycles)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error getting learning dashboard", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/shutdown")
async def shutdown_learning_controller(
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Shutdown the learning controller"""
    try:
        await controller.shutdown()
        
        return {
            "status": "success",
            "message": "Imperium Learning Controller shutdown successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Error shutting down learning controller", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/internet-learning/trigger")
async def trigger_internet_learning(
    background_tasks: BackgroundTasks,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Trigger internet-based learning for all AIs"""
    try:
        background_tasks.add_task(controller.periodic_internet_learning)
        return {
            "status": "success",
            "message": "Internet-based learning triggered for all AIs",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error triggering internet-based learning", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/internet-learning/agent/{agent_id}")
async def trigger_agent_internet_learning(
    agent_id: str,
    topic: str,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Trigger internet-based learning for a specific agent and topic"""
    try:
        result = await controller.internet_based_learning(agent_id, topic)
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error triggering internet-based learning for {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/internet-learning/log")
async def get_internet_learning_log(
    limit: int = 20,
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Get recent internet-based learning events"""
    try:
        log = controller.get_internet_learning_log(limit)
        return {
            "log": log,
            "limit": limit,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting internet learning log", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/internet-learning/impact")
async def get_internet_learning_impact(
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Get impact analysis of internet-based learning on agent metrics"""
    try:
        impact = controller.get_internet_learning_impact()
        return {
            "impact": impact,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting internet learning impact", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/ws/internet-learning")
async def websocket_internet_learning(websocket: WebSocket):
    await websocket.accept()
    controller = await get_learning_controller()
    controller._websocket_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        controller._websocket_clients.discard(websocket)


@router.post("/agents/{agent_id}/topics")
async def add_agent_topic(
    agent_id: str,
    topic_data: Dict[str, Any] = Body(...),
    controller: ImperiumLearningController = Depends(get_learning_controller)
):
    """Add a new topic for a specific AI agent to learn"""
    try:
        topic = topic_data.get("topic")
        if not topic:
            raise HTTPException(status_code=400, detail="Missing topic")
        topics = controller.get_agent_topics(agent_id)
        if topic not in topics:
            topics.append(topic)
            controller.set_agent_topics(agent_id, topics)
        return {
            "status": "success",
            "message": f"Topic '{topic}' added for agent {agent_id}",
            "topics": topics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error adding topic for agent {agent_id}", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trusted-sources")
async def list_trusted_sources():
    """List all trusted sources"""
    try:
        sources = trusted_sources.get_trusted_sources()
        return {"trusted_sources": sources, "count": len(sources)}
    except Exception as e:
        logger.error("Error listing trusted sources", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trusted-sources")
async def add_trusted_source(data: dict):
    """Add a new trusted source (url in body)"""
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")
    try:
        added = trusted_sources.add_trusted_source(url)
        if added:
            return {"status": "success", "message": f"Added trusted source: {url}"}
        else:
            return {"status": "exists", "message": f"Source already exists: {url}"}
    except Exception as e:
        logger.error("Error adding trusted source", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/trusted-sources")
async def remove_trusted_source(data: dict):
    """Remove a trusted source (url in body)"""
    url = data.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Missing 'url' in request body")
    try:
        removed = trusted_sources.remove_trusted_source(url)
        if removed:
            return {"status": "success", "message": f"Removed trusted source: {url}"}
        else:
            return {"status": "not_found", "message": f"Source not found: {url}"}
    except Exception as e:
        logger.error("Error removing trusted source", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/internet-learning/interval")
async def get_internet_learning_interval():
    """Get the periodic internet learning interval (seconds)"""
    interval = ImperiumLearningController.get_internet_learning_interval()
    return {"interval": interval}


@router.post("/internet-learning/interval")
async def set_internet_learning_interval(data: dict):
    """Set the periodic internet learning interval (seconds)"""
    interval = data.get("interval")
    if not isinstance(interval, int) or interval < 1:
        raise HTTPException(status_code=400, detail="'interval' must be a positive integer (seconds)")
    ImperiumLearningController.set_internet_learning_interval(interval)
    return {"status": "success", "interval": interval}


@router.get("/internet-learning/topics")
async def get_internet_learning_topics():
    """Get all agent topics for periodic internet learning"""
    topics = ImperiumLearningController.get_all_agent_topics()
    return {"topics": topics}


@router.post("/internet-learning/topics")
async def set_internet_learning_topics(data: dict):
    """Set all agent topics for periodic internet learning (body: {topics: {agent_id: [topics]}})"""
    topics = data.get("topics")
    if not isinstance(topics, dict):
        raise HTTPException(status_code=400, detail="'topics' must be a dict of agent_id to list of topics")
    ImperiumLearningController.set_all_agent_topics(topics)
    return {"status": "success", "topics": topics} 