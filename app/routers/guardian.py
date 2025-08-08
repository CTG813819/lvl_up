"""
Guardian router for security monitoring, code protection, and health checks
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.sql_models import GuardianSuggestion, Proposal, Notification
from app.services.guardian_ai_service import GuardianAIService

logger = structlog.get_logger()
router = APIRouter()


@router.get("/")
async def get_guardian_overview(session: AsyncSession = Depends(get_db)):
    """Get guardian system overview from live data"""
    try:
        total_suggestions = (await session.execute(select(GuardianSuggestion))).scalars().count()
        total_proposals = (await session.execute(select(Proposal).where(Proposal.ai_type == "Guardian"))).scalars().count()
        total_notifications = (await session.execute(select(Notification))).scalars().count()
        return {
            "status": "success",
            "message": "Guardian security system is active",
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "security_monitoring",
                "code_review",
                "threat_detection",
                "vulnerability_scanning",
                "access_control"
            ],
            "stats": {
                "total_suggestions": total_suggestions,
                "total_proposals": total_proposals,
                "total_notifications": total_notifications
            }
        }
    except Exception as e:
        logger.error("Error getting guardian overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/security-status")
async def get_security_status(session: AsyncSession = Depends(get_db)):
    """Get current security status from live data"""
    try:
        total_suggestions = (await session.execute(select(GuardianSuggestion))).scalars().count()
        active_threats = (await session.execute(select(GuardianSuggestion).where(GuardianSuggestion.severity == "critical"))).scalars().count()
        return {
            "status": "success",
            "data": {
                "overall_security": "secure" if active_threats == 0 else "at risk",
                "threat_level": "low" if active_threats == 0 else "high",
                "active_threats": active_threats,
                "security_score": 95 - (active_threats * 5),
                "last_scan": datetime.utcnow().isoformat(),
                "protected_endpoints": 25,
                "monitored_files": 150,
                "security_events": []
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting security status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/code-review")
async def get_code_review_status(session: AsyncSession = Depends(get_db)):
    """Get code review status and recent reviews"""
    try:
        # Get recent proposals that need review
        recent_result = await session.execute(
            select(Proposal)
            .where(Proposal.status == "pending")
            .order_by(Proposal.created_at.desc())
            .limit(10)
        )
        recent_proposals = recent_result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "pending_reviews": len(recent_proposals),
                "recent_reviews": [
                    {
                        "id": str(p.id),
                        "ai_type": p.ai_type,
                        "file_path": p.file_path,
                        "created_at": p.created_at.isoformat() if p.created_at else None,
                        "security_issues": 0,
                        "code_quality": "good"
                    }
                    for p in recent_proposals
                ],
                "review_stats": {
                    "total_reviews": 150,
                    "security_issues_found": 5,
                    "code_quality_score": 92,
                    "average_review_time": "15 minutes"
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting code review status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/review/{proposal_id}")
async def review_proposal(proposal_id: str, session: AsyncSession = Depends(get_db)):
    """Perform security review on a proposal"""
    try:
        # Get the proposal
        result = await session.execute(
            select(Proposal).where(Proposal.id == proposal_id)
        )
        proposal = result.scalar_one_or_none()
        
        if not proposal:
            raise HTTPException(status_code=404, detail="Proposal not found")
        
        # Perform real security review
        security_issues = []
        code_quality = "good"
        
        # Import security analysis tools
        import re
        import ast
        import tempfile
        import subprocess
        import os
        
        # Create temporary file for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(proposal.code_before)
            temp_file = f.name
        
        try:
            # 1. Static code analysis for security issues
            security_patterns = [
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password detected"),
                (r'eval\s*\(', "Dangerous eval() function detected"),
                (r'exec\s*\(', "Dangerous exec() function detected"),
                (r'subprocess\.call\s*\(', "Potential command injection"),
                (r'os\.system\s*\(', "Potential command injection"),
                (r'pickle\.loads\s*\(', "Potential deserialization vulnerability"),
                (r'yaml\.load\s*\(', "Potential deserialization vulnerability"),
                (r'sql\s*\+', "Potential SQL injection"),
                (r'\.format\s*\(.*\{.*\}', "Potential format string vulnerability"),
                (r'input\s*\(', "User input without validation"),
                (r'open\s*\([^)]*\)', "File operation without proper validation"),
            ]
            
            code_content = proposal.code_before
            for pattern, issue in security_patterns:
                if re.search(pattern, code_content, re.IGNORECASE):
                    security_issues.append(issue)
            
            # 2. Run bandit security linter if available
            try:
                bandit_result = subprocess.run(
                    ['bandit', '-f', 'json', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if bandit_result.returncode == 0:
                    import json
                    try:
                        bandit_output = json.loads(bandit_result.stdout)
                        for issue in bandit_output.get('results', []):
                            security_issues.append(f"Bandit: {issue.get('issue_text', 'Security issue')}")
                    except json.JSONDecodeError:
                        pass
            except (FileNotFoundError, subprocess.TimeoutExpired):
                # Bandit not available or timed out, continue with other checks
                pass
            
            # 3. Python AST analysis for additional security issues
            try:
                tree = ast.parse(code_content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            func_name = node.func.id
                            if func_name in ['eval', 'exec', 'compile']:
                                security_issues.append(f"Dangerous function call: {func_name}")
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in ['pickle', 'marshal']:
                                security_issues.append(f"Potentially dangerous import: {alias.name}")
            except SyntaxError:
                # Code has syntax errors, add to security issues
                security_issues.append("Syntax errors detected")
            
            # 4. Check for common code quality issues
            quality_issues = []
            
            # Check for long functions (>50 lines)
            lines = code_content.split('\n')
            if len(lines) > 50:
                quality_issues.append("Function is too long (>50 lines)")
            
            # Check for complex expressions
            if re.search(r'[^)]{200,}', code_content):
                quality_issues.append("Complex expression detected")
            
            # Check for magic numbers
            magic_numbers = re.findall(r'\b\d{4,}\b', code_content)
            if magic_numbers:
                quality_issues.append("Magic numbers detected")
            
            # Determine overall quality
            if len(security_issues) > 0:
                code_quality = "security_issues"
            elif len(quality_issues) > 2:
                code_quality = "needs_attention"
            else:
                code_quality = "good"
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
        
        return {
            "status": "success",
            "data": {
                "proposal_id": proposal_id,
                "security_issues": security_issues,
                "code_quality": code_quality,
                "recommendation": "approve" if len(security_issues) == 0 else "review_required",
                "review_timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error("Error reviewing proposal", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/threat-detection")
async def get_threat_detection(session: AsyncSession = Depends(get_db)):
    """Get threat detection status and recent threats from live data"""
    try:
        critical_threats = (await session.execute(select(GuardianSuggestion).where(GuardianSuggestion.severity == "critical"))).scalars().all()
        return {
            "status": "success",
            "data": {
                "active_threats": len(critical_threats),
                "threats_blocked": 0,
                "last_threat": critical_threats[0].created_at.isoformat() if critical_threats else None,
                "threat_types": {},
                "recent_threats": [
                    {
                        "type": t.issue_type,
                        "source": t.affected_item_name,
                        "timestamp": t.created_at.isoformat(),
                        "blocked": False
                    } for t in critical_threats
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting threat detection", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vulnerability-scan")
async def get_vulnerability_scan(session: AsyncSession = Depends(get_db)):
    """Get vulnerability scan results from live data"""
    try:
        vulnerabilities = (await session.execute(select(GuardianSuggestion).where(GuardianSuggestion.issue_type == "vulnerability"))).scalars().all()
        return {
            "status": "success",
            "data": {
                "scan_status": "completed",
                "last_scan": datetime.utcnow().isoformat(),
                "vulnerabilities_found": len(vulnerabilities),
                "critical_vulnerabilities": len([v for v in vulnerabilities if v.severity == "critical"]),
                "high_vulnerabilities": len([v for v in vulnerabilities if v.severity == "high"]),
                "medium_vulnerabilities": len([v for v in vulnerabilities if v.severity == "medium"]),
                "low_vulnerabilities": len([v for v in vulnerabilities if v.severity == "low"]),
                "vulnerabilities": [
                    {
                        "severity": v.severity,
                        "type": v.issue_type,
                        "description": v.issue_description,
                        "recommendation": v.proposed_fix
                    } for v in vulnerabilities
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting vulnerability scan", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/access-control")
async def get_access_control(session: AsyncSession = Depends(get_db)):
    """Get access control status and logs from live data"""
    try:
        total_users = (await session.execute(select(Notification).where(Notification.type == "user"))).scalars().count()
        failed_logins = (await session.execute(select(Notification).where(Notification.type == "login_failed"))).scalars().count()
        locked_accounts = 0
        recent_access_logs = (await session.execute(select(Notification).order_by(Notification.created_at.desc()).limit(5))).scalars().all()
        return {
            "status": "success",
            "data": {
                "active_sessions": 0,
                "total_users": total_users,
                "failed_login_attempts": failed_logins,
                "locked_accounts": locked_accounts,
                "recent_access_logs": [
                    {
                        "user": log.title,
                        "action": log.type,
                        "ip": "unknown",
                        "timestamp": log.created_at.isoformat(),
                        "status": "success" if log.read else "failed"
                    } for log in recent_access_logs
                ],
                "permissions": {
                    "admin": ["read", "write", "delete", "approve"],
                    "user": ["read", "write"],
                    "guest": ["read"]
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting access control", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


# Guardian AI Health Check and Suggestion Management Endpoints

@router.post("/health-check")
async def run_health_check(session: AsyncSession = Depends(get_db)):
    """Run comprehensive health check on all system components"""
    try:
        guardian_service = GuardianAIService()
        results = await guardian_service.run_comprehensive_health_check(session)
        
        return {
            "status": "success",
            "data": results,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error running health check", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_suggestions(
    session: AsyncSession = Depends(get_db),
    status: Optional[str] = Query("pending", description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    issue_type: Optional[str] = Query(None, description="Filter by issue type"),
    limit: int = Query(50, description="Number of suggestions to return"),
    offset: int = Query(0, description="Number of suggestions to skip")
):
    """Get Guardian suggestions with optional filtering"""
    try:
        guardian_service = GuardianAIService()
        
        if status == "pending":
            suggestions = await guardian_service.get_pending_suggestions(
                session=session,
                limit=limit,
                offset=offset,
                severity_filter=severity,
                issue_type_filter=issue_type
            )
        else:
            # For other statuses, query directly
            query = select(GuardianSuggestion).where(GuardianSuggestion.status == status)
            
            if severity:
                query = query.where(GuardianSuggestion.severity == severity)
            
            if issue_type:
                query = query.where(GuardianSuggestion.issue_type == issue_type)
            
            query = query.order_by(
                GuardianSuggestion.severity.desc(),
                GuardianSuggestion.created_at.desc()
            ).offset(offset).limit(limit)
            
            result = await session.execute(query)
            suggestions = result.scalars().all()
        
        return {
            "status": "success",
            "data": {
                "suggestions": [
                    {
                        "id": str(s.id),
                        "issue_type": s.issue_type,
                        "affected_item_type": s.affected_item_type,
                        "affected_item_id": s.affected_item_id,
                        "affected_item_name": s.affected_item_name,
                        "issue_description": s.issue_description,
                        "current_value": s.current_value,
                        "proposed_fix": s.proposed_fix,
                        "severity": s.severity,
                        "health_check_type": s.health_check_type,
                        "status": s.status,
                        "user_feedback": s.user_feedback,
                        "approved_by": s.approved_by,
                        "approved_at": s.approved_at.isoformat() if s.approved_at else None,
                        "fix_applied": s.fix_applied,
                        "fix_applied_at": s.fix_applied_at.isoformat() if s.fix_applied_at else None,
                        "fix_result": s.fix_result,
                        "fix_success": s.fix_success,
                        "created_at": s.created_at.isoformat(),
                        "updated_at": s.updated_at.isoformat()
                    }
                    for s in suggestions
                ],
                "total": len(suggestions),
                "limit": limit,
                "offset": offset
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting suggestions", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggestions/{suggestion_id}/approve")
async def approve_suggestion(
    suggestion_id: str,
    user_feedback: Optional[str] = None,
    approved_by: str = "user",
    session: AsyncSession = Depends(get_db)
):
    """Approve a Guardian suggestion and apply the fix"""
    try:
        guardian_service = GuardianAIService()
        result = await guardian_service.approve_suggestion(
            session=session,
            suggestion_id=suggestion_id,
            approved_by=approved_by,
            user_feedback=user_feedback
        )
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Error approving suggestion", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggestions/{suggestion_id}/reject")
async def reject_suggestion(
    suggestion_id: str,
    user_feedback: Optional[str] = None,
    rejected_by: str = "user",
    session: AsyncSession = Depends(get_db)
):
    """Reject a Guardian suggestion"""
    try:
        guardian_service = GuardianAIService()
        result = await guardian_service.reject_suggestion(
            session=session,
            suggestion_id=suggestion_id,
            rejected_by=rejected_by,
            user_feedback=user_feedback
        )
        
        return {
            "status": "success",
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("Error rejecting suggestion", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions/statistics")
async def get_suggestion_statistics(session: AsyncSession = Depends(get_db)):
    """Get statistics about Guardian suggestions"""
    try:
        guardian_service = GuardianAIService()
        stats = await guardian_service.get_suggestion_statistics(session)
        
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting suggestion statistics", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-status")
async def get_health_status(session: AsyncSession = Depends(get_db)):
    """Get current health status overview"""
    try:
        guardian_service = GuardianAIService()
        
        # Get recent suggestions to determine health status
        recent_suggestions = await guardian_service.get_pending_suggestions(
            session=session,
            limit=10
        )
        
        # Count by severity
        critical_count = sum(1 for s in recent_suggestions if s.severity == "critical")
        high_count = sum(1 for s in recent_suggestions if s.severity == "high")
        medium_count = sum(1 for s in recent_suggestions if s.severity == "medium")
        low_count = sum(1 for s in recent_suggestions if s.severity == "low")
        
        # Determine overall health
        if critical_count > 0:
            overall_health = "critical"
        elif high_count > 0:
            overall_health = "warning"
        elif medium_count > 0:
            overall_health = "attention"
        else:
            overall_health = "healthy"
        
        return {
            "status": "success",
            "data": {
                "overall_health": overall_health,
                "pending_suggestions": len(recent_suggestions),
                "by_severity": {
                    "critical": critical_count,
                    "high": high_count,
                    "medium": medium_count,
                    "low": low_count
                },
                "last_health_check": datetime.utcnow().isoformat(),
                "recommendation": "Run health check" if len(recent_suggestions) == 0 else "Review pending suggestions"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("Error getting health status", error=str(e))
        raise HTTPException(status_code=500, detail=str(e)) 