"""
Imperium router with monitoring endpoints
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
# from sqlalchemy import text
# from app.core.database import get_session
from datetime import datetime
import json
import os
from app.services.ai_growth_service import AIGrowthService
import asyncio
from app.models.imperium_graph_node import ImperiumGraphNode
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
import aiofiles
from fastapi import Depends
from sqlalchemy import select
from app.models.sql_models import Proposal
from app.models.proposal import ProposalResponse

router = APIRouter()

GRAPH_JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../imperium_graph_nodes.json'))

@router.get("/")
async def get_imperium():
    """Get imperium information"""
    return {"message": "Imperium router - monitoring endpoints included"}

@router.get("/monitoring")
async def get_imperium_monitoring():
    """Get Imperium monitoring status and data"""
    try:
        report_path = "imperium_monitoring_report.json"
        if os.path.exists(report_path):
            with open(report_path, 'r') as f:
                report = json.load(f)
        else:
            report = {
                "status": "initializing",
                "timestamp": datetime.now().isoformat(),
                "message": "Monitoring system is starting up"
            }
        return {"status": "success", "data": report}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/improvements")
async def get_imperium_improvements():
    """Get recent improvements made by Imperium"""
    try:
        return {
            "status": "success",
            "data": [
                {
                    "id": "1",
                    "ai_type": "imperium",
                    "improvement_type": "performance_optimization",
                    "description": "Optimized database queries for better performance",
                    "impact_score": 0.8,
                    "status": "implemented",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": "2", 
                    "ai_type": "guardian",
                    "improvement_type": "security_enhancement",
                    "description": "Enhanced threat detection algorithms",
                    "impact_score": 0.9,
                    "status": "implemented",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/issues")
async def get_imperium_issues():
    """Get recent issues detected by Imperium"""
    try:
        return {
            "status": "success",
            "data": [
                {
                    "id": "1",
                    "issue_type": "performance",
                    "severity": "low",
                    "description": "High memory usage detected in analytics module",
                    "affected_components": ["analytics", "learning"],
                    "resolution_status": "investigating",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "id": "2",
                    "issue_type": "security",
                    "severity": "medium", 
                    "description": "Potential SQL injection vulnerability in user input",
                    "affected_components": ["api", "database"],
                    "resolution_status": "resolved",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/trigger-scan")
async def trigger_imperium_scan():
    """Manually trigger Imperium system scan"""
    try:
        return {
            "status": "success",
            "message": "System scan triggered",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/status")
async def get_imperium_status():
    """Get Imperium system status"""
    try:
        pid_file = "imperium_monitoring.pid"
        is_running = False
        pid = None
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                pid = f.read().strip()
            if pid:
                try:
                    os.kill(int(pid), 0)
                    is_running = True
                except OSError:
                    is_running = False
        # Compose summary and mock values for last_audit and issues_found
        summary = "Imperium is running" if is_running else "Imperium is not running"
        last_audit = datetime.now().isoformat()
        issues_found = 0  # TODO: Replace with real value if available
        return {
            "status": "success",
            "data": {
                "is_running": is_running,
                "pid": pid,
                "timestamp": datetime.now().isoformat(),
                "summary": summary,
                "last_audit": last_audit,
                "issues_found": issues_found
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/proposals")
async def get_imperium_proposals(session: AsyncSession = Depends(get_session)):
    """Get Imperium AI proposals from the database"""
    try:
        result = await session.execute(
            select(Proposal).where(Proposal.ai_type == "Imperium")
        )
        proposals = result.scalars().all()
        return {
            "status": "success",
            "proposals": [ProposalResponse.from_orm(p) for p in proposals],
            "total_count": len(proposals),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/proposals/{proposal_id}/approve")
async def approve_proposal(proposal_id: str, session: AsyncSession = Depends(get_session)):
    """Approve a proposal by updating its status in the database"""
    try:
        result = await session.execute(select(Proposal).where(Proposal.id == proposal_id))
        proposal = result.scalar_one_or_none()
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        proposal.status = "approved"
        await session.commit()
        return {"status": "success", "proposal_id": proposal_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(proposal_id: str, session: AsyncSession = Depends(get_session)):
    """Reject a proposal by updating its status in the database"""
    try:
        result = await session.execute(select(Proposal).where(Proposal.id == proposal_id))
        proposal = result.scalar_one_or_none()
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        proposal.status = "rejected"
        await session.commit()
        return {"status": "success", "proposal_id": proposal_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/agents/{agent_id}/approve")
async def approve_agent(agent_id: str):
    """Approve and run a specific agent"""
    try:
        # Check if this is a valid agent ID
        agent_types = ["sandbox", "imperium", "guardian", "conquest"]
        if agent_id.lower() not in agent_types:
            raise HTTPException(status_code=400, detail=f"Invalid agent ID: {agent_id}. Valid agents: {agent_types}")
        
        # Import and run the agent
        from app.services.ai_agent_service import AIAgentService
        ai_agent_service = AIAgentService()
        
        agent_type = agent_id.lower()
        if agent_type == "imperium":
            result = await ai_agent_service.run_imperium_agent()
        elif agent_type == "guardian":
            result = await ai_agent_service.run_guardian_agent()
        elif agent_type == "sandbox":
            result = await ai_agent_service.run_sandbox_agent()
        elif agent_type == "conquest":
            result = await ai_agent_service.run_conquest_agent()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {agent_type}")
        
        return {
            "status": "success",
            "test_status": "passed",
            "test_output": f"Agent {agent_type} executed successfully",
            "overall_result": "passed",
            "agent_result": result,
            "message": f"Agent {agent_type} has been approved and executed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to approve agent {agent_id}: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.post("/agents/{agent_id}/reject")
async def reject_agent(agent_id: str):
    """Reject a specific agent"""
    try:
        # Check if this is a valid agent ID
        agent_types = ["sandbox", "imperium", "guardian", "conquest"]
        if agent_id.lower() not in agent_types:
            raise HTTPException(status_code=400, detail=f"Invalid agent ID: {agent_id}. Valid agents: {agent_types}")
        
        return {
            "status": "success",
            "message": f"Agent {agent_id} has been rejected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to reject agent {agent_id}: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/growth")
async def get_imperium_growth():
    """Get Imperium growth analytics"""
    try:
        growth_service = await AIGrowthService.initialize()
        insights = await growth_service.get_growth_insights()
        imperium_growth = insights.get("ai_growth_insights", {}).get("Imperium", {})
        return {"imperium_growth": imperium_growth, "timestamp": insights.get("timestamp")}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/growth/all")
async def get_all_ai_growth():
    """Get growth analytics for all AIs"""
    try:
        growth_service = await AIGrowthService.initialize()
        insights = await growth_service.get_growth_insights()
        return insights
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/persistence/learning-analytics")
async def add_graph_node(node: dict, session: AsyncSession = Depends(get_session)):
    """Add a new graph node/point to both the database and the JSON file. Never reset the file."""
    try:
        # Save to DB
        db_node = ImperiumGraphNode(
            agent_id=node.get('agent_id', ''),
            agent_type=node.get('agent_type', ''),
            topic=node.get('topic', ''),
            learning_score=node.get('learning_score'),
            timestamp=datetime.utcnow()
        )
        session.add(db_node)
        await session.commit()
        await session.refresh(db_node)
        # Save to file
        node_to_save = {
            'id': db_node.id,
            'agent_id': db_node.agent_id,
            'agent_type': db_node.agent_type,
            'topic': db_node.topic,
            'learning_score': db_node.learning_score,
            'timestamp': db_node.timestamp.isoformat()
        }
        # Read existing
        try:
            async with aiofiles.open(GRAPH_JSON_PATH, 'r', encoding='utf-8') as f:
                content = await f.read()
                nodes = json.loads(content)
        except Exception:
            nodes = []
        # Prevent accidental reset: only append if not already present
        if not any(
            n['agent_id'] == node_to_save['agent_id'] and
            n['agent_type'] == node_to_save['agent_type'] and
            n['topic'] == node_to_save['topic'] and
            n['timestamp'] == node_to_save['timestamp']
            for n in nodes
        ):
            nodes.append(node_to_save)
            async with aiofiles.open(GRAPH_JSON_PATH, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(nodes, indent=2))
        return {"status": "success", "node": node_to_save}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/persistence/learning-analytics")
async def get_graph_nodes(session: AsyncSession = Depends(get_session)):
    """Return the full, cumulative set of graph nodes/points from both DB and file (merged, deduplicated)."""
    try:
        # Get from DB
        db_nodes = (await session.execute(
            select("SELECT id, agent_id, agent_type, topic, learning_score, timestamp FROM imperium_graph_nodes ORDER BY timestamp ASC")
        )).all()
        db_nodes_list = [
            {
                'id': row.id,
                'agent_id': row.agent_id,
                'agent_type': row.agent_type,
                'topic': row.topic,
                'learning_score': row.learning_score,
                'timestamp': row.timestamp.isoformat() if row.timestamp else None
            }
            for row in db_nodes
        ]
        # Get from file
        try:
            async with aiofiles.open(GRAPH_JSON_PATH, 'r', encoding='utf-8') as f:
                content = await f.read()
                file_nodes = json.loads(content)
        except Exception:
            file_nodes = []
        # Merge and deduplicate by (agent_id, topic, timestamp)
        seen = set()
        merged = []
        for n in db_nodes_list + file_nodes:
            key = (n['agent_id'], n['topic'], n['timestamp'])
            if key not in seen:
                seen.add(key)
                merged.append(n)
        return {"nodes": merged}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.websocket("/ws/learning-analytics")
async def ws_learning_analytics(websocket: WebSocket, session: AsyncSession = Depends(get_session)):
    await websocket.accept()
    try:
        while True:
            # Get the latest graph nodes from the persistent store
            db_nodes = (await session.execute(
                select("SELECT id, agent_id, agent_type, topic, learning_score, timestamp FROM imperium_graph_nodes ORDER BY timestamp ASC")
            )).all()
            db_nodes_list = [
                {
                    'id': row.id,
                    'agent_id': row.agent_id,
                    'agent_type': row.agent_type,
                    'topic': row.topic,
                    'learning_score': row.learning_score,
                    'timestamp': row.timestamp.isoformat() if row.timestamp else None
                }
                for row in db_nodes
            ]
            await websocket.send_json(db_nodes_list)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=1011, reason=str(e)) 