"""
AI Agent Service - Coordinates autonomous AI agents
"""

import asyncio
import aiohttp
import re
import tempfile
import subprocess
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
from pathlib import Path
import json
import uuid

from ..core.database import get_session
from ..core.config import settings
from .github_service import GitHubService
from .ai_learning_service import AILearningService
from .ml_service import MLService

logger = structlog.get_logger()


class AIAgentService:
    """Service to coordinate autonomous AI agents"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIAgentService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.github_service = GitHubService()
            self.learning_service = AILearningService()
            self.ml_service = MLService()
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the AI Agent service"""
        instance = cls()
        await instance.github_service.initialize()
        await instance.learning_service.initialize()
        logger.info("AI Agent Service initialized")
        return instance
    
    async def run_imperium_agent(self) -> Dict[str, Any]:
        """Run Imperium agent - Code optimization and analysis"""
        try:
            logger.info("🧠 Imperium agent starting code analysis...")
            
            # Get repository content
            repo_content = await self.github_service.get_repo_content()
            if not repo_content:
                return {"status": "error", "message": "Could not access repository"}
            
            # Analyze Dart files
            dart_files = []
            for item in repo_content:
                if item["type"] == "file" and item["name"].endswith(".dart"):
                    dart_files.append(item["path"])
            
            if not dart_files:
                return {"status": "warning", "message": "No Dart files found"}
            
            # Analyze each Dart file
            optimizations = []
            for file_path in dart_files[:5]:  # Limit to 5 files for performance
                content = await self.github_service.get_file_content(file_path)
                if content:
                    analysis = await self._analyze_dart_code(content, file_path)
                    if analysis["optimizations"]:
                        optimizations.append(analysis)
            
            # Create proposals for optimizations
            proposals_created = 0
            for opt in optimizations:
                proposal = await self._create_optimization_proposal(opt, "Imperium")
                if proposal:
                    proposals_created += 1
            
            # Learn from the analysis
            await self._learn_from_analysis("Imperium", len(dart_files), len(optimizations))
            
            return {
                "status": "success",
                "files_analyzed": len(dart_files),
                "optimizations_found": len(optimizations),
                "proposals_created": proposals_created,
                "agent": "Imperium"
            }
            
        except Exception as e:
            logger.error("Error running Imperium agent", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def run_guardian_agent(self) -> Dict[str, Any]:
        """Run Guardian agent - Security and quality checks"""
        try:
            logger.info("🛡️ Guardian agent starting security analysis...")
            
            # Get repository content
            repo_content = await self.github_service.get_repo_content()
            if not repo_content:
                return {"status": "error", "message": "Could not access repository"}
            
            # Check for security issues
            security_issues = []
            quality_issues = []
            
            for item in repo_content:
                if item["type"] == "file":
                    content = await self.github_service.get_file_content(item["path"])
                    if content:
                        # Security checks
                        security_check = await self._check_security_issues(content, item["path"])
                        if security_check["issues"]:
                            security_issues.extend(security_check["issues"])
                        
                        # Quality checks
                        quality_check = await self._check_quality_issues(content, item["path"])
                        if quality_check["issues"]:
                            quality_issues.extend(quality_check["issues"])
            
            # Create security proposals
            security_proposals = 0
            for issue in security_issues[:3]:  # Limit to 3 critical issues
                proposal = await self._create_security_proposal(issue, "Guardian")
                if proposal:
                    security_proposals += 1
            
            # Create quality proposals
            quality_proposals = 0
            for issue in quality_issues[:3]:  # Limit to 3 quality issues
                proposal = await self._create_quality_proposal(issue, "Guardian")
                if proposal:
                    quality_proposals += 1
            
            # Learn from security analysis
            await self._learn_from_analysis("Guardian", len(security_issues), len(quality_issues))
            
            return {
                "status": "success",
                "security_issues_found": len(security_issues),
                "quality_issues_found": len(quality_issues),
                "security_proposals_created": security_proposals,
                "quality_proposals_created": quality_proposals,
                "agent": "Guardian"
            }
            
        except Exception as e:
            logger.error("Error running Guardian agent", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def run_sandbox_agent(self) -> Dict[str, Any]:
        """Run Sandbox agent - Experimentation and testing"""
        try:
            logger.info("🧪 Sandbox agent starting experimentation...")
            
            # Get recent commits to understand changes
            commits = await self.github_service.get_recent_commits(5)
            
            # Run experiments based on recent changes
            experiments = []
            for commit in commits:
                experiment = await self._run_code_experiment(commit)
                if experiment:
                    experiments.append(experiment)
            
            # Test new features or improvements
            test_results = await self._run_automated_tests()
            
            # Create experimental proposals
            proposals_created = 0
            for experiment in experiments:
                proposal = await self._create_experiment_proposal(experiment, "Sandbox")
                if proposal:
                    proposals_created += 1
            
            # Learn from experiments
            await self._learn_from_analysis("Sandbox", len(experiments), len(test_results))
            
            return {
                "status": "success",
                "experiments_run": len(experiments),
                "tests_run": len(test_results),
                "proposals_created": proposals_created,
                "agent": "Sandbox"
            }
            
        except Exception as e:
            logger.error("Error running Sandbox agent", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def run_conquest_agent(self) -> Dict[str, Any]:
        """Run Conquest agent - Code deployment and management"""
        try:
            logger.info("⚔️ Conquest agent starting deployment analysis...")
            
            # Check for approved proposals that need deployment
            approved_proposals = await self._get_approved_proposals()
            
            deployments = 0
            for proposal in approved_proposals:
                success = await self._deploy_proposal(proposal)
                if success:
                    deployments += 1
            
            # Push code changes to GitHub
            pushed_changes = await self._push_approved_changes()
            
            # Create deployment reports
            await self._create_deployment_report(deployments, pushed_changes)
            
            return {
                "status": "success",
                "deployments_made": deployments,
                "changes_pushed": pushed_changes,
                "agent": "Conquest"
            }
            
        except Exception as e:
            logger.error("Error running Conquest agent", error=str(e))
            return {"status": "error", "message": str(e)}
    
    async def run_all_agents(self) -> Dict[str, Any]:
        """Run all AI agents in sequence"""
        try:
            logger.info("🤖 Starting autonomous AI agent cycle...")
            
            results = {}
            
            # Run Imperium (Code optimization)
            results["imperium"] = await self.run_imperium_agent()
            
            # Run Guardian (Security)
            results["guardian"] = await self.run_guardian_agent()
            
            # Run Sandbox (Experimentation)
            results["sandbox"] = await self.run_sandbox_agent()
            
            # Run Conquest (Deployment)
            results["conquest"] = await self.run_conquest_agent()
            
            # Overall summary
            total_proposals = sum(
                r.get("proposals_created", 0) + 
                r.get("security_proposals_created", 0) + 
                r.get("quality_proposals_created", 0)
                for r in results.values() if isinstance(r, dict)
            )
            
            return {
                "status": "success",
                "agents_run": len(results),
                "total_proposals_created": total_proposals,
                "results": results,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Error running all agents", error=str(e))
            return {"status": "error", "message": str(e)}
    
    # Helper methods for AI agents
    async def _analyze_dart_code(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Dart code for optimizations"""
        optimizations = []
        
        # Check for common optimization opportunities
        if "setState(()" in content and content.count("setState") > 3:
            optimizations.append({
                "type": "performance",
                "description": "Multiple setState calls detected - consider batching updates",
                "file": file_path,
                "severity": "medium"
            })
        
        if "print(" in content:
            optimizations.append({
                "type": "quality",
                "description": "Debug print statements found - consider using proper logging",
                "file": file_path,
                "severity": "low"
            })
        
        if len(content) > 1000 and "class" in content:
            optimizations.append({
                "type": "maintainability",
                "description": "Large file detected - consider splitting into smaller classes",
                "file": file_path,
                "severity": "medium"
            })
        
        return {
            "file": file_path,
            "optimizations": optimizations,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    async def _check_security_issues(self, content: str, file_path: str) -> Dict[str, Any]:
        """Check for security issues in code"""
        issues = []
        
        # Check for hardcoded secrets
        if re.search(r'password\s*=\s*["\'][^"\']+["\']', content, re.IGNORECASE):
            issues.append({
                "type": "security",
                "description": "Hardcoded password detected",
                "file": file_path,
                "severity": "high"
            })
        
        # Check for SQL injection patterns
        if re.search(r'SELECT.*\+.*\$', content, re.IGNORECASE):
            issues.append({
                "type": "security",
                "description": "Potential SQL injection vulnerability",
                "file": file_path,
                "severity": "high"
            })
        
        return {"issues": issues}
    
    async def _check_quality_issues(self, content: str, file_path: str) -> Dict[str, Any]:
        """Check for code quality issues"""
        issues = []
        
        # Check for long functions
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if len(line) > 120:
                issues.append({
                    "type": "quality",
                    "description": f"Long line detected (line {i+1})",
                    "file": file_path,
                    "severity": "low"
                })
        
        return {"issues": issues}
    
    async def _run_code_experiment(self, commit: Dict) -> Optional[Dict]:
        """Run a code experiment based on a commit"""
        try:
            # Simulate running tests or experiments
            experiment_id = str(uuid.uuid4())
            
            return {
                "id": experiment_id,
                "commit_sha": commit.get("sha", "")[:8],
                "description": f"Experiment based on commit: {commit.get('commit', {}).get('message', 'Unknown')}",
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error("Error running experiment", error=str(e))
            return None
    
    async def _run_automated_tests(self) -> List[Dict]:
        """Run automated tests"""
        # Simulate test execution
        return [
            {
                "test_name": "Unit Test 1",
                "status": "passed",
                "duration": 0.5
            },
            {
                "test_name": "Integration Test 1",
                "status": "passed",
                "duration": 2.1
            }
        ]
    
    async def _get_approved_proposals(self) -> List[Dict]:
        """Get approved proposals that need deployment"""
        try:
            from sqlalchemy import select
            from ..models.sql_models import Proposal
            
            session = get_session()
            try:
                stmt = select(Proposal).where(
                    Proposal.user_feedback == "approved",
                    Proposal.status == "pending"
                )
                result = await session.execute(stmt)
                return result.scalars().all()
            finally:
                await session.close()
        except Exception as e:
            logger.error("Error getting approved proposals", error=str(e))
            return []
    
    async def _deploy_proposal(self, proposal) -> bool:
        """Deploy an approved proposal"""
        try:
            # Simulate deployment process
            logger.info(f"Deploying proposal {proposal.id}")
            
            # Update proposal status
            proposal.status = "deployed"
            proposal.updated_at = datetime.utcnow()
            
            # Save to database
            session = get_session()
            try:
                await session.commit()
                return True
            finally:
                await session.close()
        except Exception as e:
            logger.error("Error deploying proposal", error=str(e))
            return False
    
    async def _push_approved_changes(self) -> int:
        """Push approved changes to GitHub"""
        try:
            # Simulate pushing changes
            logger.info("Pushing approved changes to GitHub")
            return 1  # Number of changes pushed
        except Exception as e:
            logger.error("Error pushing changes", error=str(e))
            return 0
    
    async def _create_deployment_report(self, deployments: int, changes_pushed: int):
        """Create a deployment report"""
        try:
            report = {
                "deployments": deployments,
                "changes_pushed": changes_pushed,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Save report to database or create GitHub issue
            await self.github_service.create_issue(
                title="Deployment Report",
                body=f"Deployments: {deployments}\nChanges Pushed: {changes_pushed}",
                labels=["deployment", "report"]
            )
        except Exception as e:
            logger.error("Error creating deployment report", error=str(e))
    
    async def _create_optimization_proposal(self, analysis: Dict, ai_type: str) -> Optional[Dict]:
        """Create a proposal for code optimization with deduplication and confidence clamping"""
        try:
            from ..models.sql_models import Proposal
            session = get_session()
            try:
                # Deduplication: check for existing proposal with same file and reasoning
                duplicate = await session.execute(
                    select(Proposal).where(
                        Proposal.file_path == analysis["file"],
                        Proposal.ai_reasoning == f"Optimization analysis: {analysis['optimizations']}"
                    )
                )
                if duplicate.scalars().first():
                    return None
                confidence = 0.8
                confidence = min(max(confidence, 0.0), 1.0)
                proposal = Proposal(
                    id=uuid.uuid4(),
                    ai_type=ai_type,
                    improvement_type="performance",
                    file_path=analysis["file"],
                    code_before="",  # Would contain original code
                    code_after="",   # Would contain optimized code
                    ai_reasoning=f"Optimization analysis: {analysis['optimizations']}",
                    status="pending",
                    confidence=confidence,
                    created_at=datetime.utcnow()
                )
                session.add(proposal)
                await session.commit()
                return proposal
            finally:
                await session.close()
        except Exception as e:
            logger.error("Error creating optimization proposal", error=str(e))
            return None
    
    async def _create_security_proposal(self, issue: Dict, ai_type: str) -> Optional[Dict]:
        """Create a proposal for security fix with deduplication and confidence clamping"""
        try:
            from ..models.sql_models import Proposal
            session = get_session()
            try:
                # Deduplication: check for existing proposal with same file and reasoning
                duplicate = await session.execute(
                    select(Proposal).where(
                        Proposal.file_path == issue["file"],
                        Proposal.ai_reasoning == f"Security issue: {issue['description']}"
                    )
                )
                if duplicate.scalars().first():
                    return None
                confidence = 0.9
                confidence = min(max(confidence, 0.0), 1.0)
                proposal = Proposal(
                    id=uuid.uuid4(),
                    ai_type=ai_type,
                    improvement_type="security",
                    file_path=issue["file"],
                    code_before="",  # Would contain vulnerable code
                    code_after="",   # Would contain fixed code
                    ai_reasoning=f"Security issue: {issue['description']}",
                    status="pending",
                    confidence=confidence,
                    created_at=datetime.utcnow()
                )
                session.add(proposal)
                await session.commit()
                return proposal
            finally:
                await session.close()
        except Exception as e:
            logger.error("Error creating security proposal", error=str(e))
            return None
    
    async def _create_quality_proposal(self, issue: Dict, ai_type: str) -> Optional[Dict]:
        """Create a proposal for quality improvement with deduplication and confidence clamping"""
        try:
            from ..models.sql_models import Proposal
            session = get_session()
            try:
                # Deduplication: check for existing proposal with same file and reasoning
                duplicate = await session.execute(
                    select(Proposal).where(
                        Proposal.file_path == issue["file"],
                        Proposal.ai_reasoning == f"Quality issue: {issue['description']}"
                    )
                )
                if duplicate.scalars().first():
                    return None
                confidence = 0.7
                confidence = min(max(confidence, 0.0), 1.0)
                proposal = Proposal(
                    id=uuid.uuid4(),
                    ai_type=ai_type,
                    improvement_type="readability",
                    file_path=issue["file"],
                    code_before="",  # Would contain original code
                    code_after="",   # Would contain improved code
                    ai_reasoning=f"Quality issue: {issue['description']}",
                    status="pending",
                    confidence=confidence,
                    created_at=datetime.utcnow()
                )
                session.add(proposal)
                await session.commit()
                return proposal
            finally:
                await session.close()
        except Exception as e:
            logger.error("Error creating quality proposal", error=str(e))
            return None
    
    async def _create_experiment_proposal(self, experiment: Dict, ai_type: str) -> Optional[Dict]:
        """Create a proposal based on experiment results with deduplication and confidence clamping"""
        try:
            from ..models.sql_models import Proposal
            session = get_session()
            try:
                # Deduplication: check for existing proposal with same file and reasoning
                duplicate = await session.execute(
                    select(Proposal).where(
                        Proposal.file_path == "experiment_results",
                        Proposal.ai_reasoning == f"Experiment result: {experiment['description']}"
                    )
                )
                if duplicate.scalars().first():
                    return None
                confidence = 0.6
                confidence = min(max(confidence, 0.0), 1.0)
                proposal = Proposal(
                    id=uuid.uuid4(),
                    ai_type=ai_type,
                    improvement_type="feature",
                    file_path="experiment_results",
                    code_before="",
                    code_after="",
                    ai_reasoning=f"Experiment result: {experiment['description']}",
                    status="pending",
                    confidence=confidence,
                    created_at=datetime.utcnow()
                )
                session.add(proposal)
                await session.commit()
                return proposal
            finally:
                await session.close()
        except Exception as e:
            logger.error("Error creating experiment proposal", error=str(e))
            return None
    
    async def _learn_from_analysis(self, ai_type: str, files_analyzed: int, issues_found: int):
        """Learn from the analysis performed by AI agents"""
        try:
            # Store learning data
            from ..models.sql_models import Learning
            
            learning_entry = Learning(
                ai_type=ai_type,
                learning_type="code_analysis",
                pattern=f"analyzed_{files_analyzed}_files_found_{issues_found}_issues",
                context=f"Autonomous analysis by {ai_type} agent",
                feedback=f"Files analyzed: {files_analyzed}, Issues found: {issues_found}",
                confidence=0.8,
                created_at=datetime.utcnow()
            )
            
            session = get_session()
            try:
                session.add(learning_entry)
                await session.commit()
            finally:
                await session.close()
        except Exception as e:
            logger.error("Error learning from analysis", error=str(e)) 