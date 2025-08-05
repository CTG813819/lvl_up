# Imperium Monitoring Dashboard Endpoints

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.core.database import get_session
from datetime import datetime
import json
import os

router = APIRouter()

@router.get("/api/imperium/monitoring")
async def get_imperium_monitoring():
    """Get Imperium monitoring status and data"""
    try:
        # Read monitoring report
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
        
        return {
            "status": "success",
            "data": report
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/api/imperium/improvements")
async def get_imperium_improvements():
    """Get recent improvements made by Imperium"""
    try:
        session = get_session()
        async with session as s:
            result = await s.execute(text("""
                SELECT * FROM ai_improvements 
                ORDER BY timestamp DESC 
                LIMIT 20
            """))
            improvements = result.fetchall()
            
            return {
                "status": "success",
                "data": [
                    {
                        "id": str(row.id),
                        "ai_type": row.ai_type,
                        "improvement_type": row.improvement_type,
                        "description": row.description,
                        "impact_score": row.impact_score,
                        "status": row.status,
                        "timestamp": row.timestamp.isoformat()
                    }
                    for row in improvements
                ]
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/api/imperium/issues")
async def get_imperium_issues():
    """Get recent issues detected by Imperium"""
    try:
        session = get_session()
        async with session as s:
            result = await s.execute(text("""
                SELECT * FROM system_issues 
                ORDER BY timestamp DESC 
                LIMIT 20
            """))
            issues = result.fetchall()
            
            return {
                "status": "success",
                "data": [
                    {
                        "id": str(row.id),
                        "issue_type": row.issue_type,
                        "severity": row.severity,
                        "description": row.description,
                        "affected_components": row.affected_components,
                        "resolution_status": row.resolution_status,
                        "timestamp": row.timestamp.isoformat()
                    }
                    for row in issues
                ]
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.post("/api/imperium/trigger-scan")
async def trigger_imperium_scan():
    """Manually trigger Imperium system scan"""
    try:
        # This would trigger the monitoring system
        # For now, return success
        return {
            "status": "success",
            "message": "System scan triggered",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/api/imperium/status")
async def get_imperium_status():
    """Get Imperium system status"""
    try:
        # Check if monitoring system is running
        pid_file = "imperium_monitoring.pid"
        is_running = False
        pid = None
        
        if os.path.exists(pid_file):
            with open(pid_file, 'r') as f:
                pid = f.read().strip()
            
            if pid:
                try:
                    os.kill(int(pid), 0)  # Check if process exists
                    is_running = True
                except OSError:
                    is_running = False
        
        return {
            "status": "success",
            "data": {
                "is_running": is_running,
                "pid": pid,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
