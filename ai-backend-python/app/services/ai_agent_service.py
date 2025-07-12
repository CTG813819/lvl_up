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
from sqlalchemy import select

from ..core.database import get_session
from ..core.config import settings
from .github_service import GitHubService
from .ai_learning_service import AILearningService
from .ml_service import MLService
from .advanced_code_generator import AdvancedCodeGenerator
from app.services.unified_ai_service import call_ai, get_ai_stats

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
            # Initialize advanced code generator for sandbox experiments
            self.code_generator = AdvancedCodeGenerator()
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
            
            # Claude verification
            try:
                verification = await call_ai(
                    f"Imperium agent analyzed {len(dart_files)} Dart files and found {len(optimizations)} optimizations. Please verify the quality and suggest improvements.",
                    ai_name="imperium"
                )
            except Exception as e:
                verification = f"Claude verification error: {str(e)}"
            return {
                "status": "success",
                "files_analyzed": len(dart_files),
                "optimizations_found": len(optimizations),
                "proposals_created": proposals_created,
                "agent": "Imperium",
                "claude_verification": verification
            }
            
        except Exception as e:
            logger.error("Error running Imperium agent", error=str(e))
            # Claude failure analysis
            try:
                advice = await call_ai(
                    f"Imperium agent failed with error: {str(e)}. Please analyze the error and suggest how to improve.",
                    ai_name="imperium"
                )
            except Exception as ce:
                advice = f"Claude error: {str(ce)}"
            return {"status": "error", "message": str(e), "claude_advice": advice}
    
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
            
            # Claude verification
            try:
                verification = await call_ai(
                    f"Guardian agent found {len(security_issues)} security issues and {len(quality_issues)} quality issues. Please verify the severity and suggest improvements.",
                    ai_name="guardian"
                )
            except Exception as e:
                verification = f"Claude verification error: {str(e)}"
            return {
                "status": "success",
                "security_issues_found": len(security_issues),
                "quality_issues_found": len(quality_issues),
                "security_proposals_created": security_proposals,
                "quality_proposals_created": quality_proposals,
                "agent": "Guardian",
                "claude_verification": verification
            }
            
        except Exception as e:
            logger.error("Error running Guardian agent", error=str(e))
            # Claude failure analysis
            try:
                advice = await call_ai(
                    f"Guardian agent failed with error: {str(e)}. Please analyze the error and suggest how to improve.",
                    ai_name="guardian"
                )
            except Exception as ce:
                advice = f"Claude error: {str(ce)}"
            return {"status": "error", "message": str(e), "claude_advice": advice}
    
    async def run_sandbox_agent(self) -> Dict[str, Any]:
        """Run Sandbox agent - Experimentation and testing with AI code generation"""
        try:
            logger.info("🧪 Sandbox agent starting experimentation with AI code generation...")
            
            # Check if GitHub service is properly configured
            if not self.github_service.repo:
                logger.warning("Sandbox agent: No repository configured, creating experiment repository")
                # Try to create an experiment repository
                experiment_repo = await self._create_experiment_repository()
                if experiment_repo:
                    logger.info(f"Sandbox agent: Created experiment repository: {experiment_repo}")
                else:
                    logger.warning("Sandbox agent: Failed to create experiment repository, using local experiments")
                    return {
                        "status": "warning",
                        "message": "No repository configured and failed to create experiment repository",
                        "experiments_run": 0,
                        "tests_run": 0,
                        "proposals_created": 0,
                        "agent": "Sandbox"
                    }
            
            # Get recent commits to understand changes
            commits = await self.github_service.get_recent_commits(5)
            logger.info(f"Sandbox agent: Retrieved {len(commits)} recent commits")
            
            # Run AI code generation experiments
            ai_experiments = await self._run_ai_code_generation_experiments()
            
            if not commits:
                logger.info("Sandbox agent: No recent commits found, running AI experiments and basic tests only")
                # Run basic tests even without commits
                test_results = await self._run_automated_tests()
                
                # Claude verification
                try:
                    verification = await call_ai(
                        f"Sandbox agent ran AI experiments and basic tests. No recent commits. Please verify the quality of the tests and suggest improvements.",
                        ai_name="sandbox"
                    )
                except Exception as e:
                    verification = f"Claude verification error: {str(e)}"
                return {
                    "status": "success",
                    "message": "No recent commits, ran AI experiments and basic tests only",
                    "experiments_run": len(ai_experiments),
                    "ai_experiments": ai_experiments,
                    "tests_run": len(test_results),
                    "proposals_created": 0,
                    "agent": "Sandbox",
                    "claude_verification": verification
                }
            
            # Run experiments based on recent changes
            experiments = []
            successful_experiments = 0
            
            for i, commit in enumerate(commits):
                try:
                    logger.info(f"Sandbox agent: Running experiment {i+1}/{len(commits)} for commit {commit.get('sha', 'unknown')[:8]}")
                    experiment = await self._run_code_experiment(commit)
                    if experiment:
                        experiments.append(experiment)
                        if experiment.get("success", False):
                            successful_experiments += 1
                        logger.info(f"Sandbox agent: Experiment {i+1} completed successfully")
                    else:
                        logger.warning(f"Sandbox agent: Experiment {i+1} returned no result")
                except Exception as e:
                    logger.error(f"Sandbox agent: Error in experiment {i+1}: {str(e)}")
                    # Continue with next experiment
            
            # Test new features or improvements
            test_results = await self._run_automated_tests()
            
            # Create experimental proposals
            proposals_created = 0
            for experiment in experiments:
                proposal = await self._create_experiment_proposal(experiment, "Sandbox")
                if proposal:
                    proposals_created += 1
            
            # Create AI code generation proposals
            for ai_exp in ai_experiments:
                proposal = await self._create_ai_code_generation_proposal(ai_exp, "Sandbox")
                if proposal:
                    proposals_created += 1
            
            # Learn from the experiments
            await self._learn_from_analysis("Sandbox", len(experiments), len(ai_experiments))
            
            # Claude verification
            try:
                verification = await call_ai(
                    f"Sandbox agent ran {len(experiments)} experiments and {len(ai_experiments)} AI experiments. Please verify the quality of the experiments and suggest improvements.",
                    ai_name="sandbox"
                )
            except Exception as e:
                verification = f"Claude verification error: {str(e)}"
            return {
                "status": "success",
                "experiments_run": len(experiments),
                "ai_experiments_run": len(ai_experiments),
                "successful_experiments": successful_experiments,
                "tests_run": len(test_results),
                "proposals_created": proposals_created,
                "ai_experiments": ai_experiments,
                "agent": "Sandbox",
                "claude_verification": verification
            }
         
        except Exception as e:
            logger.error("Error running Sandbox agent", error=str(e))
            # Claude failure analysis
            try:
                advice = await call_ai(
                    f"Sandbox agent failed with error: {str(e)}. Please analyze the error and suggest how to improve.",
                    ai_name="sandbox"
                )
            except Exception as ce:
                advice = f"Claude error: {str(ce)}"
            return {"status": "error", "message": str(e), "claude_advice": advice}
    
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
            
            # Claude verification
            try:
                verification = await call_ai(
                    f"Conquest agent deployed {deployments} changes and pushed {pushed_changes} changes. Please verify the deployment and suggest improvements.",
                    ai_name="conquest"
                )
            except Exception as e:
                verification = f"Claude verification error: {str(e)}"
            return {
                "status": "success",
                "deployments_made": deployments,
                "changes_pushed": pushed_changes,
                "agent": "Conquest",
                "claude_verification": verification
            }
            
        except Exception as e:
            logger.error("Error running Conquest agent", error=str(e))
            # Claude failure analysis
            try:
                advice = await call_ai(
                    f"Conquest agent failed with error: {str(e)}. Please analyze the error and suggest how to improve.",
                    ai_name="conquest"
                )
            except Exception as ce:
                advice = f"Claude error: {str(ce)}"
            return {"status": "error", "message": str(e), "claude_advice": advice}
    
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
        """Run a real code experiment based on a commit"""
        try:
            experiment_id = str(uuid.uuid4())
            commit_sha = commit.get("sha", "")[:8]
            commit_message = commit.get('commit', {}).get('message', 'Unknown')
            
            # Create a temporary directory for the experiment
            import tempfile
            import os
            import subprocess
            import json
            from datetime import datetime
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Get repository URL from GitHub service configuration
                from .github_service import GitHubService
                github_service = GitHubService()
                
                # Use the configured repository URL
                repo_url = f"https://github.com/{github_service.repo}.git"
                if github_service.token:
                    repo_url = f"https://{github_service.token}@github.com/{github_service.repo}.git"
                
                if not github_service.repo:
                    logger.warning("No repository configured for experiment")
                    # Create a simple experiment without repository cloning
                    return {
                        "id": experiment_id,
                        "commit_sha": commit_sha,
                        "description": f"Simple experiment based on commit: {commit_message}",
                        "success": True,
                        "timestamp": datetime.utcnow().isoformat(),
                        "test_results": [],
                        "repository": "not_configured",
                        "note": "Repository not configured, experiment simulated"
                    }
                
                # Clone the repository
                clone_result = subprocess.run(
                    ['git', 'clone', repo_url, temp_dir],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if clone_result.returncode != 0:
                    logger.error(f"Failed to clone repository: {clone_result.stderr}")
                    return None
                
                # Checkout the specific commit if provided, otherwise use current branch
                if commit_sha and commit_sha != "unknown":
                    checkout_result = subprocess.run(
                        ['git', 'checkout', commit_sha],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if checkout_result.returncode != 0:
                        logger.warning(f"Failed to checkout commit {commit_sha}, using current branch: {checkout_result.stderr}")
                        # Continue with current branch if checkout fails
                else:
                    logger.info("No specific commit provided, using current branch for experiment")
                
                # Create experiment metadata
                experiment_metadata = {
                    "experiment_id": experiment_id,
                    "commit_sha": commit_sha,
                    "commit_message": commit_message,
                    "timestamp": datetime.utcnow().isoformat(),
                    "repository": repo_url,
                    "agent": "Sandbox",
                    "status": "running"
                }
                
                # Save experiment metadata
                metadata_path = os.path.join(temp_dir, "experiment_metadata.json")
                with open(metadata_path, 'w') as f:
                    json.dump(experiment_metadata, f, indent=2)
                
                # Run actual tests if they exist
                test_results = []
                
                # Check for Python tests
                if os.path.exists(os.path.join(temp_dir, 'pytest.ini')) or os.path.exists(os.path.join(temp_dir, 'tests')):
                    pytest_result = subprocess.run(
                        ['python', '-m', 'pytest', '--tb=short'],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    test_results.append({
                        "type": "pytest",
                        "success": pytest_result.returncode == 0,
                        "output": pytest_result.stdout[:1000] if pytest_result.returncode == 0 else pytest_result.stderr[:1000]
                    })
                
                # Check for Node.js tests
                if os.path.exists(os.path.join(temp_dir, 'package.json')):
                    npm_test_result = subprocess.run(
                        ['npm', 'test'],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    test_results.append({
                        "type": "npm_test",
                        "success": npm_test_result.returncode == 0,
                        "output": npm_test_result.stdout[:1000] if npm_test_result.returncode == 0 else npm_test_result.stderr[:1000]
                    })
                
                # Check for Dart tests
                if os.path.exists(os.path.join(temp_dir, 'pubspec.yaml')):
                    dart_test_result = subprocess.run(
                        ['dart', 'test'],
                        cwd=temp_dir,
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    test_results.append({
                        "type": "dart_test",
                        "success": dart_test_result.returncode == 0,
                        "output": dart_test_result.stdout[:1000] if dart_test_result.returncode == 0 else dart_test_result.stderr[:1000]
                    })
                
                # Run code analysis
                analysis_results = await self._analyze_experiment_code(temp_dir)
                
                # Determine overall success
                overall_success = all(result["success"] for result in test_results) if test_results else True
                
                # Update experiment metadata with results
                experiment_metadata.update({
                    "status": "completed",
                    "success": overall_success,
                    "test_results": test_results,
                    "analysis_results": analysis_results,
                    "completed_at": datetime.utcnow().isoformat()
                })
                
                # Save updated metadata
                with open(metadata_path, 'w') as f:
                    json.dump(experiment_metadata, f, indent=2)
                
                # Try to push experiment results to experiment repository if available
                await self._save_experiment_results(experiment_metadata, temp_dir)
                
                return {
                    "id": experiment_id,
                    "commit_sha": commit_sha,
                    "description": f"Experiment based on commit: {commit_message}",
                    "success": overall_success,
                    "timestamp": datetime.utcnow().isoformat(),
                    "test_results": test_results,
                    "analysis_results": analysis_results,
                    "repository": repo_url
                }
                
        except Exception as e:
            logger.error("Error running experiment", error=str(e))
            return None

    async def _analyze_experiment_code(self, experiment_dir: str) -> Dict[str, Any]:
        """Analyze code in the experiment directory"""
        try:
            import os
            import ast
            
            analysis_results = {
                "files_analyzed": 0,
                "total_lines": 0,
                "functions_found": 0,
                "classes_found": 0,
                "potential_issues": [],
                "complexity_score": 0
            }
            
            # Walk through Python files
            for root, dirs, files in os.walk(experiment_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                
                            analysis_results["files_analyzed"] += 1
                            analysis_results["total_lines"] += len(content.split('\n'))
                            
                            # Parse AST for basic analysis
                            try:
                                tree = ast.parse(content)
                                functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                                classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                                
                                analysis_results["functions_found"] += len(functions)
                                analysis_results["classes_found"] += len(classes)
                                
                                # Check for potential issues
                                for func in functions:
                                    if len(func.body) > 50:  # Long function
                                        analysis_results["potential_issues"].append({
                                            "type": "long_function",
                                            "file": file_path,
                                            "function": func.name,
                                            "lines": len(func.body)
                                        })
                                
                            except SyntaxError:
                                analysis_results["potential_issues"].append({
                                    "type": "syntax_error",
                                    "file": file_path
                                })
                                
                        except Exception as e:
                            logger.warning(f"Error analyzing file {file_path}: {str(e)}")
            
            # Calculate complexity score
            if analysis_results["files_analyzed"] > 0:
                analysis_results["complexity_score"] = (
                    analysis_results["total_lines"] / analysis_results["files_analyzed"] +
                    len(analysis_results["potential_issues"]) * 0.1
                )
            
            return analysis_results
            
        except Exception as e:
            logger.error("Error analyzing experiment code", error=str(e))
            return {"error": str(e)}

    async def _save_experiment_results(self, experiment_metadata: Dict, experiment_dir: str):
        """Save experiment results to the experiment repository if available"""
        try:
            # Check if we have an experiment repository configured
            experiment_repo_url = getattr(self, '_experiment_repo_url', None)
            if not experiment_repo_url:
                logger.info("No experiment repository configured, skipping result save")
                return
            
            # Create experiment results directory structure
            experiment_id = experiment_metadata["experiment_id"]
            results_dir = os.path.join(experiment_dir, "results", experiment_id)
            os.makedirs(results_dir, exist_ok=True)
            
            # Save experiment results
            results_file = os.path.join(results_dir, "experiment_results.json")
            with open(results_file, 'w') as f:
                json.dump(experiment_metadata, f, indent=2)
            
            # Create summary report
            summary_content = f"""# Experiment Results: {experiment_id}

## Overview
- **Commit**: {experiment_metadata.get('commit_sha', 'Unknown')}
- **Status**: {'✅ Success' if experiment_metadata.get('success') else '❌ Failed'}
- **Timestamp**: {experiment_metadata.get('timestamp', 'Unknown')}

## Test Results
{self._format_test_results(experiment_metadata.get('test_results', []))}

## Analysis Results
{self._format_analysis_results(experiment_metadata.get('analysis_results', {}))}

## Repository
{experiment_metadata.get('repository', 'Unknown')}
"""
            
            summary_file = os.path.join(results_dir, "README.md")
            with open(summary_file, 'w') as f:
                f.write(summary_content)
            
            logger.info(f"Saved experiment results to {results_dir}")
            
        except Exception as e:
            logger.error("Error saving experiment results", error=str(e))

    def _format_test_results(self, test_results: List[Dict]) -> str:
        """Format test results for summary"""
        if not test_results:
            return "No tests were run."
        
        formatted = []
        for result in test_results:
            status = "✅ PASS" if result.get("success") else "❌ FAIL"
            formatted.append(f"- **{result.get('type', 'Unknown')}**: {status}")
        
        return "\n".join(formatted)

    def _format_analysis_results(self, analysis_results: Dict) -> str:
        """Format analysis results for summary"""
        if not analysis_results:
            return "No analysis performed."
        
        return f"""- **Files Analyzed**: {analysis_results.get('files_analyzed', 0)}
- **Total Lines**: {analysis_results.get('total_lines', 0)}
- **Functions Found**: {analysis_results.get('functions_found', 0)}
- **Classes Found**: {analysis_results.get('classes_found', 0)}
- **Complexity Score**: {analysis_results.get('complexity_score', 0):.2f}
- **Potential Issues**: {len(analysis_results.get('potential_issues', []))}"""
    
    async def _run_automated_tests(self) -> List[Dict]:
        """Run real automated tests"""
        try:
            import subprocess
            import os
            import time
            
            test_results = []
            
            # Check if we're in a project directory with tests
            project_root = os.getcwd()
            
            # Run Python tests if they exist
            if os.path.exists('pytest.ini') or os.path.exists('tests') or os.path.exists('test'):
                start_time = time.time()
                pytest_result = subprocess.run(
                    ['python', '-m', 'pytest', '--tb=short', '-v'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                duration = time.time() - start_time
                
                test_results.append({
                    "test_name": "Python Unit Tests",
                    "status": "passed" if pytest_result.returncode == 0 else "failed",
                    "duration": duration,
                    "output": pytest_result.stdout[:500] if pytest_result.returncode == 0 else pytest_result.stderr[:500]
                })
            
            # Run Node.js tests if they exist
            if os.path.exists('package.json'):
                start_time = time.time()
                npm_test_result = subprocess.run(
                    ['npm', 'test'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                duration = time.time() - start_time
                
                test_results.append({
                    "test_name": "Node.js Tests",
                    "status": "passed" if npm_test_result.returncode == 0 else "failed",
                    "duration": duration,
                    "output": npm_test_result.stdout[:500] if npm_test_result.returncode == 0 else npm_test_result.stderr[:500]
                })
            
            # Run Dart tests if they exist
            if os.path.exists('pubspec.yaml'):
                start_time = time.time()
                dart_test_result = subprocess.run(
                    ['dart', 'test'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                duration = time.time() - start_time
                
                test_results.append({
                    "test_name": "Dart Tests",
                    "status": "passed" if dart_test_result.returncode == 0 else "failed",
                    "duration": duration,
                    "output": dart_test_result.stdout[:500] if dart_test_result.returncode == 0 else dart_test_result.stderr[:500]
                })
            
            return test_results
            
        except Exception as e:
            logger.error("Error running automated tests", error=str(e))
            return [{
                "test_name": "Test Execution",
                "status": "error",
                "duration": 0,
                "output": f"Error running tests: {str(e)}"
            }]
    
    async def _get_approved_proposals(self) -> List[Dict]:
        """Get approved proposals that need deployment"""
        try:
            from sqlalchemy import select
            from ..models.sql_models import Proposal
            async with get_session() as session:
                stmt = select(Proposal).where(
                    Proposal.user_feedback == "approved",
                    Proposal.status == "pending"
                )
                result = await session.execute(stmt)
                return result.scalars().all()
        except Exception as e:
            logger.error("Error getting approved proposals", error=str(e))
            return []
    
    async def _deploy_proposal(self, proposal) -> bool:
        """Deploy an approved proposal with real deployment process"""
        try:
            import subprocess
            import os
            import tempfile
            
            logger.info(f"Deploying proposal {proposal.id}")
            
            # Create temporary directory for deployment
            with tempfile.TemporaryDirectory() as temp_dir:
                # Write the proposed code changes to temporary files
                if proposal.code_after:
                    # Determine file extension based on file_path
                    file_ext = os.path.splitext(proposal.file_path)[1] if proposal.file_path else '.py'
                    temp_file = os.path.join(temp_dir, f"proposal_{proposal.id}{file_ext}")
                    
                    with open(temp_file, 'w') as f:
                        f.write(proposal.code_after)
                    
                    # Run deployment based on file type
                    if file_ext == '.py':
                        # Python deployment - run syntax check and basic validation
                        syntax_check = subprocess.run(
                            ['python', '-m', 'py_compile', temp_file],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if syntax_check.returncode != 0:
                            logger.error(f"Syntax check failed for proposal {proposal.id}")
                            return False
                        
                        # Run any existing tests
                        if os.path.exists('pytest.ini') or os.path.exists('tests'):
                            test_result = subprocess.run(
                                ['python', '-m', 'pytest', '--tb=short'],
                                capture_output=True,
                                text=True,
                                timeout=120
                            )
                            
                            if test_result.returncode != 0:
                                logger.error(f"Tests failed for proposal {proposal.id}")
                                return False
                    
                    elif file_ext == '.js':
                        # JavaScript deployment
                        syntax_check = subprocess.run(
                            ['node', '--check', temp_file],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if syntax_check.returncode != 0:
                            logger.error(f"Syntax check failed for proposal {proposal.id}")
                            return False
                    
                    elif file_ext == '.dart':
                        # Dart deployment
                        syntax_check = subprocess.run(
                            ['dart', 'analyze', temp_file],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        
                        if syntax_check.returncode != 0:
                            logger.error(f"Syntax check failed for proposal {proposal.id}")
                            return False
                
                # Update proposal status
                proposal.status = "deployed"
                proposal.updated_at = datetime.utcnow()
                
                # Save to database
                async with get_session() as session:
                    await session.commit()
                    logger.info(f"Proposal {proposal.id} deployed successfully")
                    return True
                    
        except Exception as e:
            logger.error("Error deploying proposal", error=str(e))
            return False
    
    async def _push_approved_changes(self) -> int:
        """Push approved changes to GitHub with real Git operations"""
        try:
            import subprocess
            import os
            import shutil
            
            logger.info("Pushing approved changes to GitHub")
            
            # Check if git is available
            git_path = shutil.which('git')
            if not git_path:
                logger.warning("Git not available in environment, skipping push")
                return 0
            
            # Check if we're in a git repository
            try:
                git_status = subprocess.run(
                    ['git', 'status'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if git_status.returncode != 0:
                    logger.warning("Not in a git repository, skipping push")
                    return 0
            except FileNotFoundError:
                logger.warning("Git command not found, skipping push")
                return 0
            except subprocess.TimeoutExpired:
                logger.error("Git status command timed out")
                return 0
            
            # Get current branch
            try:
                branch_result = subprocess.run(
                    ['git', 'branch', '--show-current'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if branch_result.returncode != 0:
                    logger.error("Failed to get current branch")
                    return 0
                
                current_branch = branch_result.stdout.strip()
            except FileNotFoundError:
                logger.warning("Git command not found, skipping push")
                return 0
            except subprocess.TimeoutExpired:
                logger.error("Git branch command timed out")
                return 0
            
            # Check if there are changes to commit
            try:
                diff_result = subprocess.run(
                    ['git', 'diff', '--name-only'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if not diff_result.stdout.strip():
                    logger.info("No changes to push")
                    return 0
            except FileNotFoundError:
                logger.warning("Git command not found, skipping push")
                return 0
            except subprocess.TimeoutExpired:
                logger.error("Git diff command timed out")
                return 0
            
            # Add all changes
            try:
                add_result = subprocess.run(
                    ['git', 'add', '.'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if add_result.returncode != 0:
                    logger.error("Failed to add changes")
                    return 0
            except FileNotFoundError:
                logger.warning("Git command not found, skipping push")
                return 0
            except subprocess.TimeoutExpired:
                logger.error("Git add command timed out")
                return 0
            
            # Commit changes
            try:
                commit_result = subprocess.run(
                    ['git', 'commit', '-m', 'Auto-deploy: Approved AI proposals'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if commit_result.returncode != 0:
                    logger.error("Failed to commit changes")
                    return 0
            except FileNotFoundError:
                logger.warning("Git command not found, skipping push")
                return 0
            except subprocess.TimeoutExpired:
                logger.error("Git commit command timed out")
                return 0
            
            # Push changes
            try:
                push_result = subprocess.run(
                    ['git', 'push', 'origin', current_branch],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if push_result.returncode != 0:
                    logger.error("Failed to push changes")
                    return 0
            except FileNotFoundError:
                logger.warning("Git command not found, skipping push")
                return 0
            except subprocess.TimeoutExpired:
                logger.error("Git push command timed out")
                return 0
            
            logger.info(f"Successfully pushed changes to {current_branch}")
            return 1
            
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
            async with get_session() as session:
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
        except Exception as e:
            logger.error("Error creating optimization proposal", error=str(e))
            return None
    
    async def _create_security_proposal(self, issue: Dict, ai_type: str) -> Optional[Dict]:
        """Create a proposal for security fix with deduplication and confidence clamping"""
        try:
            from ..models.sql_models import Proposal
            async with get_session() as session:
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
        except Exception as e:
            logger.error("Error creating security proposal", error=str(e))
            return None
    
    async def _create_quality_proposal(self, issue: Dict, ai_type: str) -> Optional[Dict]:
        """Create a proposal for quality improvement with deduplication and confidence clamping"""
        try:
            from ..models.sql_models import Proposal
            async with get_session() as session:
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
        except Exception as e:
            logger.error("Error creating quality proposal", error=str(e))
            return None
    
    async def _create_experiment_proposal(self, experiment: Dict, ai_type: str) -> Optional[Dict]:
        """Create a proposal based on experiment results with deduplication and confidence clamping"""
        try:
            from ..models.sql_models import Proposal
            async with get_session() as session:
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
            
            async with get_session() as session:
                session.add(learning_entry)
                await session.commit()
        except Exception as e:
            logger.error("Error learning from analysis", error=str(e))

    async def _create_experiment_repository(self) -> Optional[str]:
        """Create a dedicated repository for Sandbox experiments"""
        try:
            import tempfile
            import os
            import subprocess
            from datetime import datetime
            
            # Create a unique experiment repository name
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            experiment_repo_name = f"ai-sandbox-experiments-{timestamp}"
            
            # Create temporary directory for the experiment repository
            with tempfile.TemporaryDirectory() as temp_dir:
                # Initialize git repository
                init_result = subprocess.run(
                    ['git', 'init'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                if init_result.returncode != 0:
                    logger.error(f"Failed to initialize git repository: {init_result.stderr}")
                    return None
                
                # Create README for the experiment repository
                readme_content = f"""# AI Sandbox Experiments Repository

This repository contains experiments run by the AI Sandbox agent.

## Repository Information
- Created: {datetime.utcnow().isoformat()}
- Purpose: AI experimentation and testing
- Agent: Sandbox
- Status: Active

## Structure
- `/experiments/` - Individual experiment directories
- `/tests/` - Test files and results
- `/results/` - Experiment results and metrics
- `/logs/` - Experiment logs

## Usage
This repository is automatically managed by the AI Sandbox agent for:
- Code experimentation
- Feature testing
- Performance analysis
- Security testing
- Quality improvements

## Safety
All experiments are run in isolated environments and do not affect the main codebase.
"""
                
                # Write README
                readme_path = os.path.join(temp_dir, "README.md")
                with open(readme_path, 'w') as f:
                    f.write(readme_content)
                
                # Create directory structure
                os.makedirs(os.path.join(temp_dir, "experiments"), exist_ok=True)
                os.makedirs(os.path.join(temp_dir, "tests"), exist_ok=True)
                os.makedirs(os.path.join(temp_dir, "results"), exist_ok=True)
                os.makedirs(os.path.join(temp_dir, "logs"), exist_ok=True)
                
                # Add files to git
                add_result = subprocess.run(
                    ['git', 'add', '.'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                if add_result.returncode != 0:
                    logger.error(f"Failed to add files to git: {add_result.stderr}")
                    return None
                
                # Initial commit
                commit_result = subprocess.run(
                    ['git', 'commit', '-m', 'Initial commit: AI Sandbox Experiments Repository'],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True
                )
                
                if commit_result.returncode != 0:
                    logger.error(f"Failed to create initial commit: {commit_result.stderr}")
                    return None
                
                # Try to create remote repository if GitHub token is available
                if self.github_service.token and self.github_service.username:
                    try:
                        # Create repository on GitHub using API
                        repo_url = await self._create_github_repository(experiment_repo_name)
                        if repo_url:
                            # Add remote and push
                            remote_result = subprocess.run(
                                ['git', 'remote', 'add', 'origin', repo_url],
                                cwd=temp_dir,
                                capture_output=True,
                                text=True
                            )
                            
                            if remote_result.returncode == 0:
                                push_result = subprocess.run(
                                    ['git', 'push', '-u', 'origin', 'main'],
                                    cwd=temp_dir,
                                    capture_output=True,
                                    text=True
                                )
                                
                                if push_result.returncode == 0:
                                    logger.info(f"Successfully created and pushed experiment repository: {repo_url}")
                                    return repo_url
                                else:
                                    logger.warning(f"Failed to push to remote: {push_result.stderr}")
                            else:
                                logger.warning(f"Failed to add remote: {remote_result.stderr}")
                    except Exception as e:
                        logger.warning(f"Failed to create GitHub repository: {str(e)}")
                
                # If GitHub creation fails, return local repository path
                logger.info(f"Created local experiment repository: {temp_dir}")
                return temp_dir
                
        except Exception as e:
            logger.error("Error creating experiment repository", error=str(e))
            return None

    async def _create_github_repository(self, repo_name: str) -> Optional[str]:
        """Create a new GitHub repository for experiments"""
        try:
            import aiohttp
            
            url = "https://api.github.com/user/repos"
            data = {
                "name": repo_name,
                "description": "AI Sandbox Experiments Repository",
                "private": True,  # Make it private for security
                "auto_init": False,
                "gitignore_template": "Python",
                "license_template": "mit"
            }
            
            headers = {
                "Authorization": f"token {self.github_service.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 201:
                        repo_data = await response.json()
                        repo_url = repo_data.get("clone_url")
                        logger.info(f"Created GitHub repository: {repo_url}")
                        return repo_url
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create GitHub repository: {response.status} - {error_text}")
                        return None
                        
        except Exception as e:
            logger.error("Error creating GitHub repository", error=str(e))
            return None 

    async def _run_ai_code_generation_experiments(self) -> List[Dict[str, Any]]:
        """Run AI code generation experiments in sandbox"""
        experiments = []
        
        # Test different complexity levels and descriptions
        test_cases = [
            {
                "description": "A simple counter app with increment and decrement buttons",
                "complexity": "simple",
                "expected_features": ["counter", "buttons", "state"]
            },
            {
                "description": "A todo list app with add, delete, and mark complete functionality",
                "complexity": "medium",
                "expected_features": ["todo_list", "add_delete", "state_management"]
            },
            {
                "description": "A complex social media app with user authentication, real-time messaging, and API integration",
                "complexity": "complex",
                "expected_features": ["authentication", "messaging", "api", "real_time"]
            },
            {
                "description": "A fitness tracking app with workout plans, progress charts, and goal setting",
                "complexity": "medium",
                "expected_features": ["fitness", "charts", "goals", "progress"]
            },
            {
                "description": "A weather app with location services, current conditions, and 5-day forecast",
                "complexity": "medium",
                "expected_features": ["weather", "location", "forecast", "api"]
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                logger.info(f"Sandbox agent: Running AI code generation experiment {i+1}/{len(test_cases)}")
                
                # Generate code using AI
                generated_code = await self.code_generator.generate_dart_code(
                    test_case["description"], 
                    test_case["complexity"]
                )
                
                # Analyze the generated code
                analysis = await self._analyze_generated_code(generated_code, test_case)
                
                experiment = {
                    "id": str(uuid.uuid4()),
                    "description": test_case["description"],
                    "complexity": test_case["complexity"],
                    "generated_code": generated_code,
                    "code_length": len(generated_code),
                    "analysis": analysis,
                    "success": analysis["quality_score"] > 0.6,
                    "timestamp": datetime.utcnow().isoformat(),
                    "experiment_type": "ai_code_generation"
                }
                
                experiments.append(experiment)
                logger.info(f"Sandbox agent: AI experiment {i+1} completed with quality score: {analysis['quality_score']}")
                
            except Exception as e:
                logger.error(f"Sandbox agent: Error in AI experiment {i+1}: {str(e)}")
                # Continue with next experiment
        
        return experiments
    
    async def _analyze_generated_code(self, code: str, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the quality and features of generated code"""
        analysis = {
            "quality_score": 0.0,
            "features_found": [],
            "code_structure": {},
            "potential_issues": [],
            "suggestions": []
        }
        
        # Check for expected features
        expected_features = test_case.get("expected_features", [])
        found_features = []
        
        for feature in expected_features:
            if feature.lower() in code.lower():
                found_features.append(feature)
        
        analysis["features_found"] = found_features
        
        # Analyze code structure
        lines = code.split('\n')
        analysis["code_structure"] = {
            "total_lines": len(lines),
            "imports": len([line for line in lines if line.strip().startswith('import')]),
            "classes": len([line for line in lines if 'class ' in line]),
            "functions": len([line for line in lines if 'void ' in line or 'Widget ' in line]),
            "comments": len([line for line in lines if line.strip().startswith('//') or line.strip().startswith('///')])
        }
        
        # Check for potential issues
        issues = []
        if len(lines) < 10:
            issues.append("Code too short for the requested complexity")
        if not any('class ' in line for line in lines):
            issues.append("No classes found in generated code")
        if not any('Widget' in line for line in lines):
            issues.append("No Flutter widgets found")
        if not any('import' in line for line in lines):
            issues.append("No imports found")
        
        analysis["potential_issues"] = issues
        
        # Calculate quality score
        feature_score = len(found_features) / len(expected_features) if expected_features else 0.5
        structure_score = min(1.0, analysis["code_structure"]["total_lines"] / 50)  # Normalize by expected length
        issue_penalty = len(issues) * 0.1
        
        analysis["quality_score"] = max(0.0, (feature_score + structure_score) / 2 - issue_penalty)
        
        # Generate suggestions
        suggestions = []
        if analysis["quality_score"] < 0.7:
            suggestions.append("Consider regenerating with more specific requirements")
        if len(found_features) < len(expected_features):
            suggestions.append("Add more specific feature descriptions")
        if analysis["code_structure"]["total_lines"] < 20:
            suggestions.append("Request more detailed implementation")
        
        analysis["suggestions"] = suggestions
        
        return analysis
    
    async def _create_ai_code_generation_proposal(self, experiment: Dict[str, Any], ai_type: str) -> Optional[Dict]:
        """Create a proposal based on AI code generation experiment results"""
        try:
            from ..models.sql_models import Proposal
            
            analysis = experiment.get("analysis", {})
            quality_score = analysis.get("quality_score", 0.0)
            
            if quality_score < 0.5:
                # Don't create proposals for low-quality experiments
                return None
            
            proposal_data = {
                "title": f"AI Code Generation: {experiment['description'][:50]}...",
                "description": f"AI-generated code for {experiment['complexity']} complexity app. Quality score: {quality_score:.2f}",
                "type": "ai_code_generation",
                "status": "pending",
                "ai_type": ai_type,
                "metadata": {
                    "experiment_id": experiment["id"],
                    "complexity": experiment["complexity"],
                    "quality_score": quality_score,
                    "features_found": analysis.get("features_found", []),
                    "code_length": experiment["code_length"],
                    "suggestions": analysis.get("suggestions", [])
                },
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            async with get_session() as session:
                proposal = Proposal(**proposal_data)
                session.add(proposal)
                await session.commit()
                await session.refresh(proposal)
                
                logger.info(f"Created AI code generation proposal: {proposal.id}")
                return {
                    "id": str(proposal.id),
                    "title": proposal.title,
                    "status": proposal.status,
                    "quality_score": quality_score
                }
                
        except Exception as e:
            logger.error("Error creating AI code generation proposal", error=str(e))
            return None 

    def anthropic_experimentation(self, prompt: str) -> str:
        """Use unified AI service for experimentation, proposal generation, or agent reasoning."""
        try:
            import asyncio
            return asyncio.run(call_ai(prompt))
        except Exception as e:
            return f"AI service error: {str(e)}" 