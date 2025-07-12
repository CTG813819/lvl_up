"""
GitHub Service for AI Agents
"""

import os
import asyncio
import aiohttp
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
from pathlib import Path
import tempfile
import subprocess

from ..core.config import settings

logger = structlog.get_logger()


class GitHubService:
    """GitHub service for AI agents to interact with repositories"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GitHubService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.token = settings.github_token
            self.repo = settings.github_repo
            self.repo_url = settings.github_repo_url
            self.username = settings.github_username
            self.email = settings.github_email
            
            # Parse repository from URL if not directly set
            if not self.repo and self.repo_url:
                # Extract owner/repo from URL like https://github.com/CTG813819/Lvl_UP.git
                if "github.com" in self.repo_url:
                    parts = self.repo_url.replace("https://github.com/", "").replace(".git", "").split("/")
                    if len(parts) >= 2:
                        self.repo = f"{parts[0]}/{parts[1]}"
            
            # Fallback to username/repo if we have username but no repo
            if not self.repo and self.username:
                self.repo = f"{self.username}/Lvl_UP"
            
            self.base_url = "https://api.github.com"
            self.headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            } if self.token else {}
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the GitHub service"""
        instance = cls()
        if instance.token and instance.repo:
            logger.info("GitHub service initialized", repo=instance.repo)
        else:
            logger.warning("GitHub service initialized without token or repo")
        return instance
    
    async def get_repo_content(self, path: str = "") -> Optional[Dict]:
        """Get repository content"""
        try:
            url = f"{self.base_url}/repos/{self.repo}/contents/{path}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error("Failed to get repo content", path=path, status=response.status)
                        return None
        except Exception as e:
            logger.error("Error getting repo content", error=str(e), path=path)
            return None
    
    async def get_file_content(self, path: str) -> Optional[str]:
        """Get file content from repository"""
        try:
            content_data = await self.get_repo_content(path)
            if content_data and "content" in content_data:
                # Decode base64 content
                content = base64.b64decode(content_data["content"]).decode("utf-8")
                return content
            return None
        except Exception as e:
            logger.error("Error getting file content", error=str(e), path=path)
            return None
    
    async def create_or_update_file(self, path: str, content: str, message: str, branch: str = "main") -> bool:
        """Create or update a file in the repository"""
        try:
            url = f"{self.base_url}/repos/{self.repo}/contents/{path}"
            
            # Check if file exists
            existing_content = await self.get_repo_content(path)
            sha = existing_content.get("sha") if existing_content else None
            
            data = {
                "message": message,
                "content": base64.b64encode(content.encode()).decode(),
                "branch": branch
            }
            
            if sha:
                data["sha"] = sha
            
            async with aiohttp.ClientSession() as session:
                async with session.put(url, headers=self.headers, json=data) as response:
                    if response.status in [200, 201]:
                        logger.info("File updated successfully", path=path, message=message)
                        return True
                    else:
                        logger.error("Failed to update file", path=path, status=response.status)
                        return False
        except Exception as e:
            logger.error("Error updating file", error=str(e), path=path)
            return False
    
    async def clone_repo(self, target_dir: str = None) -> Optional[str]:
        """Clone the repository to a local directory"""
        try:
            if not target_dir:
                target_dir = tempfile.mkdtemp(prefix="ai_agents_")
            
            repo_url = f"https://github.com/{self.repo}.git"
            if self.token:
                repo_url = f"https://{self.token}@github.com/{self.repo}.git"
            
            # Clone repository
            result = subprocess.run(
                ["git", "clone", repo_url, target_dir],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("Repository cloned successfully", path=target_dir)
                return target_dir
            else:
                logger.error("Failed to clone repository", error=result.stderr)
                return None
        except Exception as e:
            logger.error("Error cloning repository", error=str(e))
            return None
    
    async def get_recent_commits(self, limit: int = 10) -> List[Dict]:
        """Get recent commits from the repository"""
        try:
            # Check if we have the required configuration
            if not self.token:
                logger.warning("GitHub token not configured, skipping commit fetch")
                return []
            
            if not self.repo:
                logger.warning("GitHub repository not configured, skipping commit fetch")
                return []
            
            url = f"{self.base_url}/repos/{self.repo}/commits"
            params = {"per_page": limit}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        commits = await response.json()
                        logger.info(f"Retrieved {len(commits)} recent commits")
                        return commits
                    elif response.status == 403:
                        logger.error("GitHub API access denied (403) - check token permissions and repository access")
                        return []
                    elif response.status == 404:
                        logger.error(f"Repository not found (404): {self.repo}")
                        return []
                    else:
                        logger.error("Failed to get commits", status=response.status)
                        return []
        except Exception as e:
            logger.error("Error getting commits", error=str(e))
            return []
    
    async def create_issue(self, title: str, body: str, labels: List[str] = None) -> Optional[Dict]:
        """Create a GitHub issue"""
        try:
            url = f"{self.base_url}/repos/{self.repo}/issues"
            data = {
                "title": title,
                "body": body
            }
            
            if labels:
                data["labels"] = labels
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=data) as response:
                    if response.status == 201:
                        issue = await response.json()
                        logger.info("Issue created successfully", issue_number=issue["number"])
                        return issue
                    else:
                        logger.error("Failed to create issue", status=response.status)
                        return None
        except Exception as e:
            logger.error("Error creating issue", error=str(e))
            return None
    
    async def get_webhook_events(self) -> List[Dict]:
        """Get recent webhook events (if configured)"""
        try:
            url = f"{self.base_url}/repos/{self.repo}/hooks"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        hooks = await response.json()
                        return hooks
                    else:
                        logger.error("Failed to get webhooks", status=response.status)
                        return []
        except Exception as e:
            logger.error("Error getting webhooks", error=str(e))
            return [] 