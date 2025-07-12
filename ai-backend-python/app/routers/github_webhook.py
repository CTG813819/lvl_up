"""
GitHub webhook router for AI agents
"""

import hmac
import hashlib
import json
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Header
import structlog

from app.services.ai_agent_service import AIAgentService
from app.services.github_service import GitHubService
from app.core.config import settings

logger = structlog.get_logger()
router = APIRouter()

ai_agent_service = AIAgentService()
github_service = GitHubService()


@router.get("/")
async def get_github_overview():
    """Get GitHub integration overview"""
    try:
        return {
            "status": "success",
            "message": "GitHub integration is active",
            "timestamp": datetime.utcnow().isoformat(),
            "features": [
                "webhook_handling",
                "repository_integration",
                "issue_management",
                "pull_request_review",
                "automated_actions"
            ]
        }
    except Exception as e:
        logger.error("Error getting GitHub overview", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """Handle GitHub webhook events"""
    try:
        # Get the raw body
        body = await request.body()
        
        # Verify webhook signature (if secret is configured)
        if settings.github_webhook_secret and x_hub_signature_256:
            if not _verify_webhook_signature(body, x_hub_signature_256, settings.github_webhook_secret):
                raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse the webhook payload
        payload = json.loads(body)
        
        logger.info("📡 GitHub webhook received", event=x_github_event)
        
        # Handle different event types
        if x_github_event == "push":
            await _handle_push_event(payload)
        elif x_github_event == "pull_request":
            await _handle_pull_request_event(payload)
        elif x_github_event == "issues":
            await _handle_issues_event(payload)
        elif x_github_event == "create":
            await _handle_create_event(payload)
        else:
            logger.info(f"Unhandled GitHub event: {x_github_event}")
        
        return {"status": "success", "event": x_github_event}
        
    except Exception as e:
        logger.error("Error handling GitHub webhook", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


async def _handle_push_event(payload: Dict[str, Any]):
    """Handle push events - trigger AI agents"""
    try:
        repository = payload.get("repository", {})
        commits = payload.get("commits", [])
        
        logger.info("🔄 Push event detected", 
                   repo=repository.get("name"),
                   commits_count=len(commits))
        
        # Trigger AI agents to analyze the changes
        result = await ai_agent_service.run_all_agents()
        
        logger.info("✅ AI agents triggered by push event", result=result)
        
        # Create a summary issue
        if commits:
            commit_messages = [commit.get("message", "") for commit in commits[:3]]
            summary = "\n".join([f"- {msg}" for msg in commit_messages])
            
            await github_service.create_issue(
                title="AI Analysis Triggered by Push",
                body=f"AI agents have been triggered to analyze recent changes:\n\n{summary}\n\nAnalysis results: {result}",
                labels=["ai-analysis", "automated"]
            )
        
    except Exception as e:
        logger.error("Error handling push event", error=str(e))


async def _handle_pull_request_event(payload: Dict[str, Any]):
    """Handle pull request events"""
    try:
        action = payload.get("action")
        pr = payload.get("pull_request", {})
        
        logger.info("🔀 Pull request event", 
                   action=action,
                   pr_number=pr.get("number"))
        
        if action in ["opened", "synchronize"]:
            # Trigger code review by AI agents
            result = await ai_agent_service.run_guardian_agent()
            
            # Create review comment
            await github_service.create_issue(
                title=f"AI Code Review - PR #{pr.get('number')}",
                body=f"AI Guardian has reviewed this pull request:\n\n{result}",
                labels=["ai-review", "code-review"]
            )
        
    except Exception as e:
        logger.error("Error handling pull request event", error=str(e))


async def _handle_issues_event(payload: Dict[str, Any]):
    """Handle issues events"""
    try:
        action = payload.get("action")
        issue = payload.get("issue", {})
        
        logger.info("📋 Issue event", 
                   action=action,
                   issue_number=issue.get("number"))
        
        if action == "opened":
            # Analyze issue and suggest solutions
            result = await ai_agent_service.run_sandbox_agent()
            
            # Add AI-generated comment to issue
            # Note: This would require GitHub API to add comments to issues
            
    except Exception as e:
        logger.error("Error handling issues event", error=str(e))


async def _handle_create_event(payload: Dict[str, Any]):
    """Handle create events (new branches, tags)"""
    try:
        ref_type = payload.get("ref_type")
        ref = payload.get("ref")
        
        logger.info("🏷️ Create event", 
                   ref_type=ref_type,
                   ref=ref)
        
        if ref_type == "branch":
            # New branch created - trigger analysis
            result = await ai_agent_service.run_imperium_agent()
            
    except Exception as e:
        logger.error("Error handling create event", error=str(e))


def _verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify GitHub webhook signature"""
    try:
        expected_signature = "sha256=" + hmac.new(
            secret.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    except Exception as e:
        logger.error("Error verifying webhook signature", error=str(e))
        return False


@router.get("/status")
async def webhook_status():
    """Get webhook status"""
    return {
        "webhook_configured": bool(settings.github_webhook_secret),
        "repository": settings.github_repo,
        "events_handled": ["push", "pull_request", "issues", "create"]
    } 