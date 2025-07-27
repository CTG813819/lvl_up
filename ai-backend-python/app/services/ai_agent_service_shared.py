"""
Updated AI Agent Service with Shared Token Limits Integration
"""

import asyncio
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime
import sys
import os

from app.services.unified_ai_service_shared import unified_ai_service_shared
from app.services.ml_service import MLService
from app.services.github_service import GitHubService

logger = structlog.get_logger()

class AIAgentServiceShared:
    """AI agent service with shared token limits integration"""
    def __init__(self):
        self.github_service = GitHubService()
        self.ml_service = MLService()
    
    async def process_request(self, ai_name: str, request_type: str, 
                             prompt: str, estimated_tokens: int = 1000) -> Dict[str, Any]:
        """Process AI request with shared limits"""
        try:
            # Try Anthropic first
            try:
                result = await self._process_with_anthropic(ai_name, request_type, prompt, estimated_tokens)
                return result
            except Exception as anthropic_error:
                logger.warning(f"Anthropic failed for {ai_name} {request_type}, trying OpenAI", error=str(anthropic_error))
                return await self._process_with_openai(ai_name, request_type, prompt, estimated_tokens)
                
        except Exception as e:
            logger.error("Error in AI agent request", error=str(e), ai_name=ai_name, request_type=request_type)
            return {
                "success": False,
                "error": "system_error",
                "message": str(e),
                "ai_name": ai_name,
                "request_type": request_type
            }
    
    async def _process_with_anthropic(self, ai_name: str, request_type: str, 
                                     prompt: str, estimated_tokens: int) -> Dict[str, Any]:
        """Process with Anthropic"""
        result = await unified_ai_service_shared.make_request(
            ai_name, prompt, estimated_tokens, 4000, 0.7
        )
        
        if result["success"]:
            return {
                "success": True,
                "provider": "anthropic",
                "content": result["content"],
                "request_type": request_type,
                "ai_name": ai_name,
                "tokens_used": result.get("tokens_used", 0)
            }
        else:
            raise Exception(result.get("message", "Anthropic processing failed"))
    
    async def _process_with_openai(self, ai_name: str, request_type: str, 
                                  prompt: str, estimated_tokens: int) -> Dict[str, Any]:
        """Process with OpenAI"""
        result = await unified_ai_service_shared.make_request(
            ai_name, prompt, estimated_tokens, 4000, 0.7
        )
        
        if result["success"]:
            return {
                "success": True,
                "provider": "openai",
                "content": result["content"],
                "request_type": request_type,
                "ai_name": ai_name,
                "tokens_used": result.get("tokens_used", 0)
            }
        else:
            return {
                "success": False,
                "error": "openai_processing_failed",
                "message": result.get("message", "OpenAI processing failed"),
                "ai_name": ai_name,
                "request_type": request_type
            }

    # --- Begin ported agent learning logic and helpers ---
    def reset_scan_state(self):
        self._scan_state = set()
        logger.info("[CYCLE] Reset scan state for new agent cycle - will scan ALL files")

    def should_scan_file(self, file_path: str) -> bool:
        return True

    def _get_heuristics_path(self, agent_name):
        import os
        heuristics_dir = os.path.join(os.path.dirname(__file__), '../heuristics')
        os.makedirs(heuristics_dir, exist_ok=True)
        return os.path.join(heuristics_dir, f'{agent_name}_heuristics.json')

    def _load_heuristics(self, agent_name, default_keywords=None):
        import os, json
        path = self._get_heuristics_path(agent_name)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if default_keywords:
                        merged = list(set(data.get('keywords', []) + default_keywords))
                        data['keywords'] = merged
                    return data
            except Exception as e:
                logger.warning(f"Failed to load heuristics for {agent_name}: {e}")
        return {'keywords': default_keywords or []}

    def _save_heuristics(self, agent_name, heuristics):
        import os, json
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
        # ... (copy the full method from ai_agent_service.py) ...
        # (already present in shared, so skip if already implemented)
        pass

    # --- Port all agent methods and helpers from ai_agent_service.py ---
    async def run_imperium_agent(self) -> dict:
        self.reset_scan_state()
        logger.info("[CYCLE] Imperium agent starting new scan, test, and proposal cycle...")
        repo_content = await self.github_service.get_repo_content()
        if not repo_content:
            return {"status": "error", "message": "Could not access repository"}
        scanned_files = await self._select_files_by_directive(repo_content, "imperium")
        logger.info(f"[DIRECTIVE] Imperium agent selected {len(scanned_files)} files: {scanned_files}")
        if not scanned_files:
            return {"status": "warning", "message": "No relevant files found for optimization"}
        optimizations = []
        for file_path in scanned_files:
            if not any(file_path.endswith(ext) for ext in ['.dart', '.py', '.js', '.ts']):
                logger.info(f"Skipping {file_path} - not a supported code file type")
                continue
            content = await self.github_service.get_file_content(file_path)
            if content:
                if file_path.endswith('.dart'):
                    analysis = await self._analyze_dart_code(content, file_path)
                elif file_path.endswith('.py'):
                    analysis = await self._analyze_python_code(content, file_path)
                elif file_path.endswith('.js'):
                    analysis = await self._analyze_js_code(content, file_path)
                else:
                    analysis = None
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

    async def run_guardian_agent(self) -> dict:
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

    async def run_sandbox_agent(self) -> dict:
        logger.info("🧪 Sandbox agent starting experiment analysis...")
        repo_content = await self.github_service.get_repo_content()
        if not repo_content:
            return {"status": "error", "message": "Could not access repository"}
        scanned_files = await self._select_files_by_directive(repo_content, "sandbox")
        logger.info(f"[DIRECTIVE] Sandbox agent selected {len(scanned_files)} files: {scanned_files}")
        if not self.github_service.repo:
            logger.warning("Sandbox agent: No repository configured, creating experiment repository")
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
        commits = await self.github_service.get_recent_commits(5)
        logger.info(f"Sandbox agent: Retrieved {len(commits)} recent commits")
        ai_experiments = await self._run_ai_code_generation_experiments()
        if not commits:
            logger.info("Sandbox agent: No recent commits found, running AI experiments and basic tests only")
            test_results = await self._run_automated_tests()
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
        test_results = await self._run_automated_tests()
        proposals_created = 0
        for experiment in experiments:
            proposal = await self._create_experiment_proposal(experiment, "Sandbox")
            if proposal:
                proposals_created += 1
        for ai_exp in ai_experiments:
            proposal = await self._create_ai_code_generation_proposal(ai_exp, "Sandbox")
            if proposal:
                proposals_created += 1
        await self._learn_from_analysis("Sandbox", len(experiments), len(ai_experiments))
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

    async def run_conquest_agent(self) -> dict:
        logger.info("⚔️ Conquest agent starting app suggestion analysis...")
        repo_content = await self.github_service.get_repo_content()
        if not repo_content:
            return {"status": "error", "message": "Could not access repository"}
        scanned_files = await self._select_files_by_directive(repo_content, "conquest")
        logger.info(f"[DIRECTIVE] Conquest agent selected {len(scanned_files)} files: {scanned_files}")
        approved_proposals = await self._get_approved_proposals()
        deployments = 0
        for proposal in approved_proposals:
            success = await self._deploy_proposal(proposal)
            if success:
                deployments += 1
        pushed_changes = await self._push_approved_changes()
        await self._create_deployment_report(deployments, pushed_changes)
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
    # --- End ported agent learning logic and helpers ---

# Global instance
ai_agent_service_shared = AIAgentServiceShared() 