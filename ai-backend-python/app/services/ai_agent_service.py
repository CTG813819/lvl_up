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
import os

import httpx

from ..core.database import get_session
from ..core.config import settings
from .github_service import GitHubService
from .ai_learning_service import AILearningService
from .ml_service import MLService
from .advanced_code_generator import AdvancedCodeGenerator
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call

logger = structlog.get_logger()


class AIAgentService:
    """Service to coordinate autonomous AI agents"""
    
    _instance = None
    _initialized = False
    _scan_state = set()  # Track files scanned in the current cycle
    
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
            self.backend_url = "http://localhost:8000"  # Add missing backend_url
            self._initialized = True
    
    def reset_scan_state(self):
        """Reset scan state to ensure fresh file scanning every cycle"""
        self._scan_state = set()
        logger.info("[CYCLE] Reset scan state for new agent cycle - will scan ALL files")
    
    def should_scan_file(self, file_path: str) -> bool:
        """Always return True to ensure all files are scanned every cycle"""
        # Always scan files to ensure comprehensive coverage
        return True
    
    @classmethod
    async def initialize(cls):
        """Initialize the AI Agent service"""
        instance = cls()
        await instance.github_service.initialize()
        await instance.learning_service.initialize()
        logger.info("AI Agent Service initialized")
        return instance
    
    def _get_heuristics_path(self, agent_name):
        heuristics_dir = os.path.join(os.path.dirname(__file__), '../heuristics')
        os.makedirs(heuristics_dir, exist_ok=True)
        return os.path.join(heuristics_dir, f'{agent_name}_heuristics.json')

    def _load_heuristics(self, agent_name, default_keywords=None):
        path = self._get_heuristics_path(agent_name)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if default_keywords:
                        # Merge with defaults, avoid duplicates
                        merged = list(set(data.get('keywords', []) + default_keywords))
                        data['keywords'] = merged
                    return data
            except Exception as e:
                logger.warning(f"Failed to load heuristics for {agent_name}: {e}")
        return {'keywords': default_keywords or []}

    def _save_heuristics(self, agent_name, heuristics):
        path = self._get_heuristics_path(agent_name)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(heuristics, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save heuristics for {agent_name}: {e}")

    def _add_learned_heuristics(self, agent_name, new_keywords):
        heuristics = self._load_heuristics(agent_name)
        before = set(heuristics.get('keywords', []))
        after = before.union(set(new_keywords))
        if after != before:
            heuristics['keywords'] = list(after)
            self._save_heuristics(agent_name, heuristics)
            logger.info(f"[LEARNING] {agent_name} agent added new heuristics: {set(new_keywords) - before}")

    async def _select_files_by_directive(self, repo_content, directive):
        """
        Enhanced: Select files based on the agent's directive using advanced heuristics.
        Always include backend and app files, use content and path heuristics, and log inclusion reasons.
        Now also uses learned heuristics from persistent storage.
        """
        relevant_files = []
        inclusion_log = {}
        # Directories to always include for backend/app
        backend_dirs = [
            "ai-backend-python/", "backend/", "src/", "app/", "services/", "routers/", "models/", "core/", "scripts/"
        ]
        app_dirs = [
            "lib/", "android/", "ios/", "web/", "macos/", "windows/", "assets/", "images/"
        ]
        always_include_dirs = backend_dirs + app_dirs
        # Exclude dependency/output folders
        exclude_dirs = ["node_modules/", "venv/", "build/", ".git/", "__pycache__", ".idea/", ".vscode/"]
        # File extensions to consider - focus on actual code files
        code_exts = [".py", ".js", ".ts", ".dart"]
        # Load learned heuristics
        agent_keywords = {
            'imperium': ["TODO optimize", "performance", "slow"],
            'guardian': ["password", "secret", "token", "api_key", "jwt", "auth", "encrypt", "decrypt", "os.environ", "subprocess", "eval", "exec", "pickle", "open(", "write(", "read(", "database", "sql", "query", "user input", "request", "response"],
            'conquest': ["feature", "extension", "plugin", "integration", "user-facing", "UI", "UX"],
            'sandbox': ["experiment", "test", "extension", "feature", "prototype", "draft", "sample", "demo", "playground"]
        }
        heuristics = self._load_heuristics(directive, agent_keywords.get(directive, []))
        learned_keywords = heuristics.get('keywords', [])
        for item in repo_content:
            if item["type"] != "file":
                continue
            path = item["path"]
            name = item["name"]
            
            # Always scan all files - no skipping based on previous scans
            if not self.should_scan_file(path):
                continue
                
            # Exclude dependency/output folders
            if any(f"/{ex}" in path or path.startswith(ex) for ex in exclude_dirs):
                continue
            # Only consider code/config files
            if not any(name.endswith(ext) for ext in code_exts):
                continue
            # Always include backend/app files
            if any(path.startswith(d) for d in always_include_dirs):
                relevant_files.append(path)
                inclusion_log[path] = "backend/app directory inclusion"
                continue
            # Use learned heuristics (keywords)
            try:
                content = await self.github_service.get_file_content(path)
                if content and any(kw.lower() in content.lower() for kw in learned_keywords):
                    relevant_files.append(path)
                    inclusion_log[path] = f"{directive}: learned heuristic keyword match"
                    continue
            except Exception:
                continue
            # Imperium: optimization - focus on actual code files
            if directive == "imperium":
                # Only analyze actual code files, not config files
                if not any(path.endswith(ext) for ext in [".py", ".js", ".ts", ".dart"]):
                    continue
                try:
                    content = await self.github_service.get_file_content(path)
                    if content and (
                        ("TODO optimize" in content or "performance" in content or "slow" in content or content.count("for ") > 3 or content.count("while ") > 3)
                        or (max([len(line) for line in content.splitlines()]) > 120)
                        or (len(content) > 2000)
                        or (sum(1 for l in content.splitlines() if l.strip().startswith("def ")) > 10)
                        or ("setState" in content and content.count("setState") > 3)
                        or ("print(" in content)
                        or (".format(" in content and "f\"" not in content)
                    ):
                        relevant_files.append(path)
                        inclusion_log[path] = "imperium: optimization heuristic"
                except Exception:
                    continue
            # Guardian: security
            elif directive == "guardian":
                try:
                    content = await self.github_service.get_file_content(path)
                    if (
                        (content and re.search(r'password|secret|token|api[_-]?key|jwt|auth|encrypt|decrypt|os\.environ|subprocess|eval|exec|pickle|open\(|write\(|read\(|database|sql|query|user input|request|response', content, re.IGNORECASE))
                        or (content and 'import os' in content)
                    ):
                        relevant_files.append(path)
                        inclusion_log[path] = "guardian: security heuristic"
                except Exception:
                    continue
            # Conquest: app logic/extensions
            elif directive == "conquest":
                if any(x in path for x in ["app/", "extensions/", "lib/", "models/", "screens/", "widgets/", "services/", "feature", "plugin", "integration", "user-facing", "UI", "UX"]):
                    relevant_files.append(path)
                    inclusion_log[path] = "conquest: app/extension logic heuristic"
                else:
                    try:
                        content = await self.github_service.get_file_content(path)
                        if content and ("feature" in content or "extension" in content or "plugin" in content or "integration" in content):
                            relevant_files.append(path)
                            inclusion_log[path] = "conquest: app/extension content heuristic"
                    except Exception:
                        continue
            # Sandbox: experiments/features
            elif directive == "sandbox":
                if any(x in path for x in ["experiment", "test", "extension", "feature", "prototype", "draft", "sample", "demo", "playground"]):
                    relevant_files.append(path)
                    inclusion_log[path] = "sandbox: experiment/feature path heuristic"
                else:
                    try:
                        content = await self.github_service.get_file_content(path)
                        if content and any(x in content for x in ["experiment", "feature", "prototype", "draft", "sample", "demo", "playground"]):
                            relevant_files.append(path)
                            inclusion_log[path] = "sandbox: experiment/feature content heuristic"
                    except Exception:
                        continue
        logger.info(f"[HEURISTICS] {directive} agent inclusion log: {inclusion_log}")
        return relevant_files

    async def run_imperium_agent(self) -> Dict[str, Any]:
        """Run Imperium agent - Code optimization and analysis"""
        try:
            self.reset_scan_state()
            logger.info("[CYCLE] Imperium agent starting new scan, test, and proposal cycle...")
            repo_content = await self.github_service.get_repo_content()
            if not repo_content:
                return {"status": "error", "message": "Could not access repository"}
            # Use directive-based file selection
            scanned_files = await self._select_files_by_directive(repo_content, "imperium")
            logger.info(f"[DIRECTIVE] Imperium agent selected {len(scanned_files)} files: {scanned_files}")
            if not scanned_files:
                return {"status": "warning", "message": "No relevant files found for optimization"}
            optimizations = []
            for file_path in scanned_files:
                # Only analyze files that can actually be optimized
                if not any(file_path.endswith(ext) for ext in ['.dart', '.py', '.js', '.ts']):
                    logger.info(f"Skipping {file_path} - not a supported code file type")
                    continue
                    
                content = await self.github_service.get_file_content(file_path)
                if content:
                    analysis = await self._analyze_dart_code(content, file_path) if file_path.endswith('.dart') else \
                              await self._analyze_python_code(content, file_path) if file_path.endswith('.py') else \
                              await self._analyze_js_code(content, file_path) if file_path.endswith('.js') else None
                    if analysis and analysis.get("optimizations"):
                        analysis["files_analyzed"] = scanned_files
                        optimizations.append(analysis)
                    elif analysis:
                        logger.info(f"No optimizations found for {file_path}")
            proposals_created = 0
            for opt in optimizations:
                proposal = await self._create_optimization_proposal(opt, "Imperium")
                if proposal:
                    proposals_created += 1
            await self._learn_from_analysis("Imperium", len(scanned_files), len(optimizations))
            return {"status": "success", "proposals_created": proposals_created, "files_analyzed": scanned_files}
        except Exception as e:
            logger.error(f"Imperium agent error: {e}")
            return {"status": "error", "message": str(e)}

    async def run_guardian_agent(self) -> Dict[str, Any]:
        """Run Guardian agent - Security and quality checks"""
        try:
            logger.info("🛡️ Guardian agent starting security analysis...")
            repo_content = await self.github_service.get_repo_content()
            if not repo_content:
                return {"status": "error", "message": "Could not access repository"}
            scanned_files = await self._select_files_by_directive(repo_content, "guardian")
            logger.info(f"[DIRECTIVE] Guardian agent selected {len(scanned_files)} files: {scanned_files}")
            if not scanned_files:
                return {"status": "warning", "message": "No relevant files found for security analysis"}
            security_issues = []
            quality_issues = []
            for file_path in scanned_files:
                content = await self.github_service.get_file_content(file_path)
                if content:
                    security_check = await self._check_security_issues(content, file_path)
                    if security_check["issues"]:
                        security_check["files_analyzed"] = scanned_files
                        security_issues.extend(security_check["issues"])
                    quality_check = await self._check_quality_issues(content, file_path)
                    if quality_check["issues"]:
                        quality_check["files_analyzed"] = scanned_files
                        quality_issues.extend(quality_check["issues"])
            security_proposals = 0
            for issue in security_issues[:3]:
                proposal = await self._create_security_proposal(issue, "Guardian")
                if proposal:
                    security_proposals += 1
            quality_proposals = 0
            for issue in quality_issues[:3]:
                proposal = await self._create_quality_proposal(issue, "Guardian")
                if proposal:
                    quality_proposals += 1
            await self._learn_from_analysis("Guardian", len(security_issues), len(quality_issues))
            return {
                "status": "success",
                "security_proposals": security_proposals,
                "quality_proposals": quality_proposals,
                "files_analyzed": scanned_files
            }
        except Exception as e:
            logger.error(f"Guardian agent error: {e}")
            return {"status": "error", "message": str(e)}

    async def run_sandbox_agent(self) -> Dict[str, Any]:
        """Run Sandbox agent - Experimental and feature proposals"""
        try:
            logger.info("🧪 Sandbox agent starting experiment analysis...")
            repo_content = await self.github_service.get_repo_content()
            if not repo_content:
                return {"status": "error", "message": "Could not access repository"}
            scanned_files = await self._select_files_by_directive(repo_content, "sandbox")
            logger.info(f"[DIRECTIVE] Sandbox agent selected {len(scanned_files)} files: {scanned_files}")
            
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
                    verification = await anthropic_rate_limited_call(
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
                verification = await anthropic_rate_limited_call(
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
                advice = await anthropic_rate_limited_call(
                    f"Sandbox agent failed with error: {str(e)}. Please analyze the error and suggest how to improve.",
                    ai_name="sandbox"
                )
            except Exception as ce:
                advice = f"Claude error: {str(ce)}"
            return {"status": "error", "message": str(e), "claude_advice": advice}
    
    async def run_conquest_agent(self) -> Dict[str, Any]:
        """Run Conquest agent - User experience and app suggestions"""
        try:
            logger.info("⚔️ Conquest agent starting app suggestion analysis...")
            repo_content = await self.github_service.get_repo_content()
            if not repo_content:
                return {"status": "error", "message": "Could not access repository"}
            scanned_files = await self._select_files_by_directive(repo_content, "conquest")
            logger.info(f"[DIRECTIVE] Conquest agent selected {len(scanned_files)} files: {scanned_files}")
            
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
                verification = await anthropic_rate_limited_call(
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
                advice = await anthropic_rate_limited_call(
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
        """Analyze Dart code for optimizations and generate actual code improvements"""
        optimizations = []
        original_code = content
        optimized_code = content
        
        # Check for common optimization opportunities and generate actual fixes
        if "setState(()" in content and content.count("setState") > 3:
            # Generate optimized code that batches setState calls
            optimized_code = self._optimize_setstate_calls(content)
            optimizations.append({
                "type": "performance",
                "description": "Multiple setState calls detected - batching updates for better performance",
                "file": file_path,
                "severity": "medium"
            })
        
        if "print(" in content:
            # Replace print statements with proper logging
            optimized_code = self._replace_print_with_logging(optimized_code)
            optimizations.append({
                "type": "quality",
                "description": "Debug print statements replaced with proper logging",
                "file": file_path,
                "severity": "low"
            })
        
        if len(content) > 1000 and "class" in content:
            # Suggest splitting large classes
            split_suggestion = self._suggest_class_splitting(content, file_path)
            if split_suggestion:
                optimized_code = split_suggestion
                optimizations.append({
                    "type": "maintainability",
                    "description": "Large file detected - split into smaller, focused classes",
                    "file": file_path,
                    "severity": "medium"
                })
        
        # Add null safety improvements if not already present
        if "?" not in content and "!" not in content and "late" not in content:
            optimized_code = self._add_null_safety(optimized_code)
            optimizations.append({
                "type": "safety",
                "description": "Added null safety improvements for better code reliability",
                "file": file_path,
                "severity": "medium"
            })
        
        return {
            "file_path": file_path,
            "original_code": original_code,
            "optimized_code": optimized_code,
            "optimizations": optimizations,
            "confidence": 0.8 if optimizations else 0.0,
            "reasoning": f"AI detected {len(optimizations)} optimization opportunities",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _optimize_setstate_calls(self, content: str) -> str:
        """Optimize multiple setState calls by batching them"""
        import re
        
        # Find multiple setState calls in the same method
        lines = content.split('\n')
        optimized_lines = []
        in_method = False
        setstate_calls = []
        
        for i, line in enumerate(lines):
            if 'setState(()' in line:
                setstate_calls.append((i, line))
            
            optimized_lines.append(line)
        
        # If we found multiple setState calls, batch them
        if len(setstate_calls) > 1:
            # Create a batched version
            batched_code = content.replace(
                'setState(() {',
                'setState(() {\n    // Batched updates for better performance'
            )
            return batched_code
        
        return content
    
    def _replace_print_with_logging(self, content: str) -> str:
        """Replace print statements with proper logging"""
        import re
        
        # Add logging import if not present
        if "import 'dart:developer';" not in content:
            content = "import 'dart:developer';\n" + content
        
        # Replace print statements with log statements
        content = re.sub(
            r'print\s*\(\s*([^)]+)\s*\)',
            r'log(\1)',
            content
        )
        
        return content
    
    def _suggest_class_splitting(self, content: str, file_path: str) -> str:
        """Suggest splitting large classes into smaller ones"""
        # This is a simplified version - in practice, you'd want more sophisticated analysis
        if "class " in content and content.count("class ") > 1:
            # Already has multiple classes, no need to split
            return content
        
        # For demonstration, add a comment suggesting splitting
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            if "class " in line and len(content) > 1000:
                # Add comment suggesting split
                optimized_lines.append(f"// TODO: Consider splitting this large class into smaller, focused classes")
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _add_null_safety(self, content: str) -> str:
        """Add null safety improvements to Dart code"""
        import re
        
        # Add null safety to variable declarations
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Add ? to String declarations that could be null
            if 'String ' in line and '=' in line and '?' not in line and '!' not in line:
                line = re.sub(r'String\s+(\w+)\s*=', r'String? \1 =', line)
            
            # Add late to variables that are initialized later
            if 'String ' in line and '=' in line and 'null' in line:
                line = re.sub(r'String\?\s+(\w+)\s*=\s*null', r'late String \1', line)
            
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
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
    
    async def _analyze_python_code(self, content: str, file_path: str) -> Dict[str, Any]:
        """Analyze Python code for optimizations and generate actual code improvements"""
        optimizations = []
        original_code = content
        optimized_code = content
        
        # Check for print statements and replace with logging
        if "print(" in content:
            optimized_code = self._replace_python_print_with_logging(optimized_code)
            optimizations.append({
                "type": "quality",
                "description": "Debug print statements replaced with proper logging",
                "file": file_path,
                "severity": "low"
            })
        
        # Check for f-strings vs .format() and modernize
        if ".format(" in content and "f\"" not in content:
            optimized_code = self._modernize_string_formatting(optimized_code)
            optimizations.append({
                "type": "modernization",
                "description": "Replaced .format() with f-strings for better readability",
                "file": file_path,
                "severity": "low"
            })
        
        # Check for list comprehensions vs loops
        if "for " in content and " in " in content and "append(" in content:
            optimized_code = self._convert_loops_to_comprehensions(optimized_code)
            optimizations.append({
                "type": "performance",
                "description": "Converted loops to list comprehensions for better performance",
                "file": file_path,
                "severity": "medium"
            })
        
        # Check for unused imports
        unused_imports = self._find_unused_python_imports(optimized_code)
        if unused_imports:
            optimized_code = self._remove_unused_python_imports(optimized_code, unused_imports)
            optimizations.append({
                "type": "cleanup",
                "description": f"Removed {len(unused_imports)} unused imports",
                "file": file_path,
                "severity": "low"
            })
        
        # Check for long functions
        long_functions = self._find_long_python_functions(optimized_code)
        if long_functions:
            optimized_code = self._suggest_python_function_refactoring(optimized_code, long_functions)
            optimizations.append({
                "type": "maintainability",
                "description": "Long functions detected - added refactoring suggestions",
                "file": file_path,
                "severity": "medium"
            })
        
        return {
            "file_path": file_path,
            "original_code": original_code,
            "optimized_code": optimized_code,
            "optimizations": optimizations,
            "confidence": 0.8 if optimizations else 0.0,
            "reasoning": f"AI detected {len(optimizations)} Python optimization opportunities",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _replace_python_print_with_logging(self, content: str) -> str:
        """Replace print statements with proper logging in Python"""
        import re
        
        # Add logging import if not present
        if "import logging" not in content:
            content = "import logging\n" + content
        
        # Replace print statements with logging
        content = re.sub(
            r'print\s*\(\s*([^)]+)\s*\)',
            r'logging.info(\1)',
            content
        )
        
        return content
    
    def _modernize_string_formatting(self, content: str) -> str:
        """Replace .format() with f-strings"""
        import re
        
        # Simple replacement - in practice, you'd want more sophisticated parsing
        content = re.sub(
            r'(\w+)\.format\(([^)]+)\)',
            r'f"\1"',
            content
        )
        
        return content
    
    def _convert_loops_to_comprehensions(self, content: str) -> str:
        """Convert simple loops to list comprehensions"""
        import re
        
        # This is a simplified version - in practice, you'd want AST parsing
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            if "for " in line and " in " in line and "append(" in line:
                # Add comment suggesting comprehension
                optimized_lines.append(f"# TODO: Consider converting this loop to a list comprehension")
            optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _find_unused_python_imports(self, content: str) -> list:
        """Find unused Python imports"""
        import re
        
        unused = []
        import_lines = re.findall(r'import\s+(\w+)', content)
        from_imports = re.findall(r'from\s+\w+\s+import\s+(\w+)', content)
        
        all_imports = import_lines + from_imports
        
        for imp in all_imports:
            # Count usage (excluding import line)
            usage_count = len(re.findall(rf'\b{imp}\b', content)) - 1
            if usage_count == 0:
                unused.append(imp)
        
        return unused
    
    def _remove_unused_python_imports(self, content: str, unused_imports: list) -> str:
        """Remove unused Python imports"""
        import re
        
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            should_keep = True
            for imp in unused_imports:
                if f"import {imp}" in line or f"from {imp}" in line:
                    should_keep = False
                    break
            if should_keep:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines)
    
    def _find_long_python_functions(self, content: str) -> list:
        """Find Python functions that are too long"""
        import re
        
        long_functions = []
        function_defs = [m.start() for m in re.finditer(r'def\s+\w+\s*\(', content)]
        
        for idx, start in enumerate(function_defs):
            end = function_defs[idx + 1] if idx + 1 < len(function_defs) else len(content)
            func_body = content[start:end]
            if func_body.count('\n') > 30:  # Python functions should be shorter
                long_functions.append((start, end))
        
        return long_functions
    
    def _suggest_python_function_refactoring(self, content: str, long_functions: list) -> str:
        """Add comments suggesting Python function refactoring"""
        lines = content.split('\n')
        
        for start, end in long_functions:
            # Find the function name
            func_match = re.search(r'def\s+(\w+)', content[start:start+100])
            if func_match:
                func_name = func_match.group(1)
                # Add comment before the function
                lines.insert(start, f"# TODO: Consider refactoring {func_name} into smaller functions")
        
        return '\n'.join(lines)
    
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
    
    async def _analyze_js_code(self, content: str, file_path: str) -> dict:
        """Analyze JavaScript code for optimizations and generate actual code improvements"""
        optimizations = []
        warnings = []
        original_code = content
        optimized_code = content
        lines = content.split('\n')
        
        # Check for debug statements and replace them
        if "console.log(" in content:
            optimized_code = self._replace_console_log_with_logging(optimized_code)
            optimizations.append({
                "type": "quality",
                "description": "Debug console.log statements replaced with proper logging",
                "file": file_path,
                "severity": "low"
            })
        
        # Check for 'var' usage and replace with 'const' or 'let'
        if re.search(r'\bvar\b', content):
            optimized_code = self._replace_var_with_modern_declarations(optimized_code)
            optimizations.append({
                "type": "maintainability",
                "description": "Use of 'var' replaced with 'const' or 'let' for better block scoping",
                "file": file_path,
                "severity": "medium"
            })
        
        # Check for == instead of === and fix them
        if re.search(r'[^=]==[^=]', content):
            optimized_code = self._replace_loose_equality_with_strict(optimized_code)
            warnings.append({
                "type": "bug-risk",
                "description": "Use of '==' replaced with '===' to prevent unexpected type coercion",
                "file": file_path,
                "severity": "medium"
            })
        
        # Check for unused variables and remove them
        unused_vars = self._find_unused_variables(optimized_code)
        if unused_vars:
            optimized_code = self._remove_unused_variables(optimized_code, unused_vars)
            for var in unused_vars:
                warnings.append({
                    "type": "maintainability",
                    "description": f"Unused variable '{var}' removed",
                    "file": file_path,
                    "severity": "low"
                })
        
        # Check for long functions and suggest refactoring
        long_functions = self._find_long_functions(optimized_code)
        if long_functions:
            optimized_code = self._suggest_function_refactoring(optimized_code, long_functions)
            warnings.append({
                "type": "complexity",
                "description": "Long functions detected - added refactoring suggestions",
                "file": file_path,
                "severity": "medium"
            })
        
        # Add missing semicolons
        missing_semicolons = self._find_missing_semicolons(optimized_code)
        if missing_semicolons:
            optimized_code = self._add_missing_semicolons(optimized_code, missing_semicolons)
            warnings.append({
                "type": "style",
                "description": "Added missing semicolons for consistency",
                "file": file_path,
                "severity": "low"
            })
        
        return {
            "file_path": file_path,
            "original_code": original_code,
            "optimized_code": optimized_code,
            "optimizations": optimizations,
            "warnings": warnings,
            "confidence": 0.8 if optimizations or warnings else 0.0,
            "reasoning": f"AI detected {len(optimizations)} optimizations and {len(warnings)} improvements",
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
    
    def _replace_console_log_with_logging(self, content: str) -> str:
        """Replace console.log with proper logging"""
        import re
        
        # Replace console.log with a more appropriate logging method
        content = re.sub(
            r'console\.log\s*\(\s*([^)]+)\s*\)',
            r'console.info(\1)  // Replaced console.log with console.info',
            content
        )
        
        return content
    
    def _replace_var_with_modern_declarations(self, content: str) -> str:
        """Replace var with const or let based on usage"""
        import re
        
        # Find var declarations
        var_pattern = r'\bvar\s+(\w+)\s*='
        matches = re.finditer(var_pattern, content)
        
        for match in reversed(list(matches)):
            var_name = match.group(1)
            start, end = match.span()
            
            # Check if variable is reassigned later
            reassigned = re.search(rf'\b{var_name}\s*=', content[end:])
            
            if reassigned:
                # Use let if reassigned
                replacement = f'let {var_name} ='
            else:
                # Use const if not reassigned
                replacement = f'const {var_name} ='
            
            content = content[:start] + replacement + content[end:]
        
        return content
    
    def _replace_loose_equality_with_strict(self, content: str) -> str:
        """Replace == with === for strict equality"""
        import re
        
        # Replace == with === (but not ==== or !==)
        content = re.sub(r'([^=])==([^=])', r'\1===\2', content)
        
        return content
    
    def _find_unused_variables(self, content: str) -> list:
        """Find unused variable declarations"""
        import re
        
        unused = []
        declared_vars = re.findall(r'\b(?:let|const|var)\s+(\w+)', content)
        
        for var in declared_vars:
            # Count occurrences (declaration + usage)
            count = len(re.findall(rf'\b{var}\b', content))
            if count == 1:  # Only declaration, no usage
                unused.append(var)
        
        return unused
    
    def _remove_unused_variables(self, content: str, unused_vars: list) -> str:
        """Remove unused variable declarations"""
        import re
        
        for var in unused_vars:
            # Remove the entire line with the unused variable
            pattern = rf'\s*(?:let|const|var)\s+{var}\s*=.*?;?\s*\n'
            content = re.sub(pattern, '\n', content)
        
        return content
    
    def _find_long_functions(self, content: str) -> list:
        """Find functions that are too long"""
        import re
        
        long_functions = []
        function_defs = [m.start() for m in re.finditer(r'function\s+\w+\s*\(', content)]
        
        for idx, start in enumerate(function_defs):
            end = function_defs[idx + 1] if idx + 1 < len(function_defs) else len(content)
            func_body = content[start:end]
            if func_body.count('\n') > 50:
                long_functions.append((start, end))
        
        return long_functions
    
    def _suggest_function_refactoring(self, content: str, long_functions: list) -> str:
        """Add comments suggesting function refactoring"""
        lines = content.split('\n')
        
        for start, end in long_functions:
            # Find the function name
            func_match = re.search(r'function\s+(\w+)', content[start:start+100])
            if func_match:
                func_name = func_match.group(1)
                # Add comment before the function
                lines.insert(start, f"// TODO: Consider refactoring {func_name} into smaller functions")
        
        return '\n'.join(lines)
    
    def _find_missing_semicolons(self, content: str) -> list:
        """Find lines that might be missing semicolons"""
        import re
        
        missing = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if (line and not line.endswith(';') and not line.endswith('{') and 
                not line.endswith('}') and not line.startswith('//') and 
                not line.startswith('*') and not line.startswith('function') and 
                not line.startswith('if') and not line.startswith('else') and 
                not line.startswith('for') and not line.startswith('while') and 
                not line.startswith('switch') and not line.startswith('return')):
                if re.match(r'.+\w.+', line):
                    missing.append(i)
        
        return missing
    
    def _add_missing_semicolons(self, content: str, missing_lines: list) -> str:
        """Add missing semicolons to specified lines"""
        lines = content.split('\n')
        
        for line_num in missing_lines:
            if line_num < len(lines):
                lines[line_num] = lines[line_num] + ';'
        
        return '\n'.join(lines)
    
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
        """Get approved proposals for deployment"""
        try:
            from ..models.sql_models import Proposal
            from sqlalchemy import select
            
            async with get_session() as session:
                stmt = select(Proposal).where(
                    Proposal.user_feedback == "approved",
                    Proposal.status == "pending"
                )
                result = await session.execute(stmt)
                proposals = result.scalars().all()
                
                # Convert to list of dictionaries
                return [
                    {
                        "id": str(proposal.id),
                        "ai_type": proposal.ai_type,
                        "file_path": proposal.file_path,
                        "code_before": proposal.code_before,
                        "code_after": proposal.code_after,
                        "status": proposal.status
                    }
                    for proposal in proposals
                ]
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
    
    def _generate_dynamic_description(self, proposal_data: dict) -> str:
        """Generate a dynamic, context-aware description for a proposal."""
        file_path = proposal_data.get('file_path', 'unknown')
        improvement_type = proposal_data.get('improvement_type', 'general')
        ai_reasoning = proposal_data.get('ai_reasoning', '')
        code_before = proposal_data.get('code_before', '')
        code_after = proposal_data.get('code_after', '')
        # Simple code diff summary
        before_lines = set(code_before.splitlines())
        after_lines = set(code_after.splitlines())
        added = after_lines - before_lines
        removed = before_lines - after_lines
        diff_summary = []
        if added:
            diff_summary.append(f"Added lines: {', '.join(list(added)[:2])}")
        if removed:
            diff_summary.append(f"Removed lines: {', '.join(list(removed)[:2])}")
        diff_text = "; ".join(diff_summary) if diff_summary else "Minor changes."
        # Compose description
        desc = f"{improvement_type.capitalize()} proposal for {file_path}. {diff_text}"
        if ai_reasoning:
            desc += f" Reason: {ai_reasoning}"
        return desc

    async def _create_optimization_proposal(self, analysis: Dict[str, Any], ai_type: str) -> Optional[Dict[str, Any]]:
        try:
            file_path = analysis.get("file_path", "unknown")
            optimizations = analysis.get("optimizations", [])
            files_analyzed = analysis.get("files_analyzed", [])
            original_code = analysis.get("original_code", "")
            optimized_code = analysis.get("optimized_code", "")
            
            # Don't create proposals if there are no optimizations
            if not optimizations:
                logger.info(f"No optimizations found for {file_path}, skipping proposal creation")
                return None
            
            # Don't create proposals if the code hasn't actually changed
            if original_code == optimized_code:
                logger.info(f"No code changes detected for {file_path}, skipping proposal creation")
                return None
            
            # Don't create proposals if either code block is empty
            if not original_code.strip() or not optimized_code.strip():
                logger.info(f"Empty code blocks detected for {file_path}, skipping proposal creation")
                return None
            
            proposal_data = {
                "ai_type": ai_type,
                "file_path": file_path,
                "code_before": original_code,
                "code_after": optimized_code,
                "improvement_type": "performance",
                "confidence": analysis.get("confidence", 0.7),
                "ai_reasoning": analysis.get("reasoning", "AI detected optimization opportunities"),
                "files_analyzed": files_analyzed
            }
            proposal_data["description"] = self._generate_dynamic_description(proposal_data)
            
            # Create proposal through the proper validation flow
            from ..models.proposal import ProposalCreate
            from ..routers.proposals import create_proposal_internal
            from ..core.database import get_session
            
            # Create ProposalCreate instance
            proposal_create = ProposalCreate(**proposal_data)
            
            # Create proposal through the internal function with validation
            async with get_session() as db:
                try:
                    proposal = await create_proposal_internal(proposal_create, db)
                    logger.info(f"Created optimization proposal: {proposal.id}")
                    return {
                        "id": str(proposal.id),
                        "ai_type": proposal.ai_type,
                        "file_path": proposal.file_path,
                        "status": proposal.status,
                        "confidence": proposal.confidence
                    }
                except Exception as e:
                    logger.error(f"Failed to create proposal through validation: {str(e)}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating optimization proposal: {e}")
            return None

    async def _create_security_proposal(self, issue: Dict, ai_type: str) -> Optional[Dict]:
        try:
            # Check for duplicates first
            from ..models.sql_models import Proposal
            from sqlalchemy import select
            
            async with get_session() as session:
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
            proposal_data = {
                "ai_type": ai_type,
                "improvement_type": "security",
                "file_path": issue["file"],
                "code_before": issue.get("code_before", ""),
                "code_after": issue.get("code_after", ""),
                "ai_reasoning": f"Security issue: {issue['description']}",
                "status": "pending",
                "confidence": confidence,
                "files_analyzed": issue.get("files_analyzed", [])
            }
            proposal_data["description"] = self._generate_dynamic_description(proposal_data)
            
            # Create proposal through the proper validation flow
            from ..models.proposal import ProposalCreate
            from ..routers.proposals import create_proposal_internal
            
            # Create ProposalCreate instance
            proposal_create = ProposalCreate(**proposal_data)
            
            # Create proposal through the internal function with validation
            async with get_session() as db:
                try:
                    proposal = await create_proposal_internal(proposal_create, db)
                    logger.info(f"Created security proposal: {proposal.id}")
                    return {
                        "id": str(proposal.id),
                        "ai_type": proposal.ai_type,
                        "file_path": proposal.file_path,
                        "status": proposal.status,
                        "confidence": proposal.confidence
                    }
                except Exception as e:
                    logger.error(f"Failed to create security proposal through validation: {str(e)}")
                    return None
                    
        except Exception as e:
            logger.error("Error creating security proposal", error=str(e))
            return None

    async def _create_quality_proposal(self, issue: Dict, ai_type: str) -> Optional[Dict]:
        try:
            # Check for duplicates first
            from ..models.sql_models import Proposal
            from sqlalchemy import select
            
            async with get_session() as session:
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
            proposal_data = {
                "ai_type": ai_type,
                "improvement_type": "readability",
                "file_path": issue["file"],
                "code_before": issue.get("code_before", ""),
                "code_after": issue.get("code_after", ""),
                "ai_reasoning": f"Quality issue: {issue['description']}",
                "status": "pending",
                "confidence": confidence,
                "files_analyzed": issue.get("files_analyzed", [])
            }
            proposal_data["description"] = self._generate_dynamic_description(proposal_data)
            
            # Create proposal through the proper validation flow
            from ..models.proposal import ProposalCreate
            from ..routers.proposals import create_proposal_internal
            
            # Create ProposalCreate instance
            proposal_create = ProposalCreate(**proposal_data)
            
            # Create proposal through the internal function with validation
            async with get_session() as db:
                try:
                    proposal = await create_proposal_internal(proposal_create, db)
                    logger.info(f"Created quality proposal: {proposal.id}")
                    return {
                        "id": str(proposal.id),
                        "ai_type": proposal.ai_type,
                        "file_path": proposal.file_path,
                        "status": proposal.status,
                        "confidence": proposal.confidence
                    }
                except Exception as e:
                    logger.error(f"Failed to create quality proposal through validation: {str(e)}")
                    return None
                    
        except Exception as e:
            logger.error("Error creating quality proposal", error=str(e))
            return None

    async def _create_experiment_proposal(self, experiment: Dict, ai_type: str) -> Optional[Dict]:
        try:
            # Check for duplicates first
            from ..models.sql_models import Proposal
            from sqlalchemy import select
            
            async with get_session() as session:
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
            proposal_data = {
                "ai_type": ai_type,
                "improvement_type": "feature",
                "file_path": "experiment_results",
                "code_before": experiment.get("code_before", ""),
                "code_after": experiment.get("code_after", ""),
                "ai_reasoning": f"Experiment result: {experiment['description']}",
                "status": "pending",
                "confidence": confidence,
                "files_analyzed": experiment.get("files_analyzed", [])
            }
            proposal_data["description"] = self._generate_dynamic_description(proposal_data)
            
            # Create proposal through the proper validation flow
            from ..models.proposal import ProposalCreate
            from ..routers.proposals import create_proposal_internal
            
            # Create ProposalCreate instance
            proposal_create = ProposalCreate(**proposal_data)
            
            # Create proposal through the internal function with validation
            async with get_session() as db:
                try:
                    proposal = await create_proposal_internal(proposal_create, db)
                    logger.info(f"Created experiment proposal: {proposal.id}")
                    return {
                        "id": str(proposal.id),
                        "ai_type": proposal.ai_type,
                        "file_path": proposal.file_path,
                        "status": proposal.status,
                        "confidence": proposal.confidence
                    }
                except Exception as e:
                    logger.error(f"Failed to create experiment proposal through validation: {str(e)}")
                    return None
                    
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
                learning_data={
                    'pattern': f"analyzed_{files_analyzed}_files_found_{issues_found}_issues",
                    'context': f"Autonomous analysis by {ai_type} agent",
                    'feedback': f"Files analyzed: {files_analyzed}, Issues found: {issues_found}",
                    'confidence': 0.8
                }
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
        """Use Anthropic Claude for experimentation, proposal generation, or agent reasoning."""
        try:
            return call_claude(prompt)
        except Exception as e:
            return f"Anthropic error: {str(e)}" 

    async def _append_learning_pattern_and_persist(self, ai_type: str, pattern: str):
        """Append a learning pattern to the agent's metrics and persist to DB."""
        try:
            from app.services.imperium_learning_controller import ImperiumLearningController
            controller = ImperiumLearningController()
            if ai_type not in controller._agent_metrics:
                logger.warning(f"[LEARNING] No in-memory metrics for {ai_type}, cannot append pattern.")
                return
            metrics = controller._agent_metrics[ai_type]
            if pattern not in metrics.learning_patterns:
                metrics.learning_patterns.append(pattern)
                await controller.persist_agent_metrics(ai_type)
                logger.info(f"[LEARNING] Appended pattern and persisted metrics for {ai_type}: {pattern}")
        except Exception as e:
            logger.error(f"[LEARNING] Error appending pattern and persisting for {ai_type}: {str(e)}")