"""
Data Collection Service - Direct API Integrations
Collects raw data from external sources using direct APIs, reducing Claude usage
"""

import asyncio
import aiohttp
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import structlog
from urllib.parse import quote
import os

from .cache_service import CacheService
from ..core.config import settings

logger = structlog.get_logger()

class DataCollectionService:
    """Service for collecting raw data from external sources using direct APIs"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataCollectionService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.cache_service = CacheService()
            self.github_token = settings.github_token
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the data collection service"""
        instance = cls()
        await instance.cache_service.initialize()
        logger.info("Data collection service initialized")
        return instance
    
    async def collect_github_data(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Collect raw data from GitHub API"""
        try:
            # Check cache first
            cached_data = await self.cache_service.get("github_data", query, max_results=max_results)
            if cached_data:
                logger.info(f"Using cached GitHub data for query: {query}")
                return cached_data
            
            # Collect fresh data
            headers = {"Accept": "application/vnd.github.v3+json"}
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
            
            # Search repositories
            repo_url = "https://api.github.com/search/repositories"
            repo_params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": min(max_results, 30)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(repo_url, headers=headers, params=repo_params) as resp:
                    if resp.status == 200:
                        repo_data = await resp.json()
                        
                        # Search code
                        code_url = "https://api.github.com/search/code"
                        code_params = {
                            "q": f"{query} language:python",
                            "per_page": min(max_results, 30)
                        }
                        
                        async with session.get(code_url, headers=headers, params=code_params) as code_resp:
                            code_data = await code_resp.json() if code_resp.status == 200 else {"items": []}
                        
                        # Combine and format results
                        results = []
                        
                        # Add repository data
                        for repo in repo_data.get("items", []):
                            results.append({
                                "type": "repository",
                                "title": repo.get("full_name"),
                                "url": repo.get("html_url"),
                                "description": repo.get("description", ""),
                                "stars": repo.get("stargazers_count", 0),
                                "language": repo.get("language", ""),
                                "created_at": repo.get("created_at"),
                                "updated_at": repo.get("updated_at"),
                                "source": "github"
                            })
                        
                        # Add code data
                        for code in code_data.get("items", []):
                            results.append({
                                "type": "code",
                                "title": code.get("name"),
                                "url": code.get("html_url"),
                                "repository": code.get("repository", {}).get("full_name", ""),
                                "path": code.get("path", ""),
                                "language": code.get("language", ""),
                                "source": "github"
                            })
                        
                        # Cache the results
                        await self.cache_service.set("github_data", query, results, max_results=max_results)
                        
                        logger.info(f"Collected {len(results)} GitHub results for query: {query}")
                        return results
                    else:
                        logger.warning(f"GitHub API error: {resp.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error collecting GitHub data: {e}")
            return []
    
    async def collect_stackoverflow_data(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Collect raw data from Stack Overflow API"""
        try:
            # Check cache first
            cached_data = await self.cache_service.get("stackoverflow_data", query, max_results=max_results)
            if cached_data:
                logger.info(f"Using cached Stack Overflow data for query: {query}")
                return cached_data
            
            # Collect fresh data
            url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                "order": "desc",
                "sort": "relevance",
                "q": query,
                "site": "stackoverflow",
                "pagesize": min(max_results, 30),
                "filter": "withbody"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        
                        results = []
                        for item in data.get("items", []):
                            results.append({
                                "type": "question",
                                "title": item.get("title", ""),
                                "url": item.get("link", ""),
                                "body": item.get("body", ""),
                                "score": item.get("score", 0),
                                "answer_count": item.get("answer_count", 0),
                                "tags": item.get("tags", []),
                                "created_at": item.get("creation_date"),
                                "last_activity": item.get("last_activity_date"),
                                "source": "stackoverflow"
                            })
                        
                        # Cache the results
                        await self.cache_service.set("stackoverflow_data", query, results, max_results=max_results)
                        
                        logger.info(f"Collected {len(results)} Stack Overflow results for query: {query}")
                        return results
                    else:
                        logger.warning(f"Stack Overflow API error: {resp.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error collecting Stack Overflow data: {e}")
            return []
    
    async def collect_arxiv_data(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Collect raw data from arXiv API"""
        try:
            # Check cache first
            cached_data = await self.cache_service.get("arxiv_data", query, max_results=max_results)
            if cached_data:
                logger.info(f"Using cached arXiv data for query: {query}")
                return cached_data
            
            # Collect fresh data
            url = "http://export.arxiv.org/api/query"
            params = {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": min(max_results, 30),
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as resp:
                    if resp.status == 200:
                        xml_data = await resp.text()
                        
                        # Simple XML parsing for arXiv data
                        results = []
                        import re
                        
                        # Extract paper entries
                        entries = re.findall(r'<entry>(.*?)</entry>', xml_data, re.DOTALL)
                        
                        for entry in entries[:max_results]:
                            title_match = re.search(r'<title>(.*?)</title>', entry)
                            summary_match = re.search(r'<summary>(.*?)</summary>', entry)
                            id_match = re.search(r'<id>(.*?)</id>', entry)
                            published_match = re.search(r'<published>(.*?)</published>', entry)
                            
                            if title_match and id_match:
                                results.append({
                                    "type": "paper",
                                    "title": title_match.group(1).strip(),
                                    "url": id_match.group(1).strip(),
                                    "summary": summary_match.group(1).strip() if summary_match else "",
                                    "published": published_match.group(1).strip() if published_match else "",
                                    "source": "arxiv"
                                })
                        
                        # Cache the results
                        await self.cache_service.set("arxiv_data", query, results, max_results=max_results)
                        
                        logger.info(f"Collected {len(results)} arXiv results for query: {query}")
                        return results
                    else:
                        logger.warning(f"arXiv API error: {resp.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error collecting arXiv data: {e}")
            return []
    
    async def collect_medium_data(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Collect raw data from Medium RSS feed"""
        try:
            # Check cache first
            cached_data = await self.cache_service.get("medium_data", query, max_results=max_results)
            if cached_data:
                logger.info(f"Using cached Medium data for query: {query}")
                return cached_data
            
            # Collect fresh data from Medium RSS
            url = "https://medium.com/feed/tag/artificial-intelligence"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        xml_data = await resp.text()
                        
                        # Simple XML parsing for Medium RSS
                        results = []
                        import re
                        
                        # Extract article entries
                        entries = re.findall(r'<item>(.*?)</item>', xml_data, re.DOTALL)
                        
                        for entry in entries[:max_results]:
                            title_match = re.search(r'<title>(.*?)</title>', entry)
                            link_match = re.search(r'<link>(.*?)</link>', entry)
                            description_match = re.search(r'<description>(.*?)</description>', entry)
                            pub_date_match = re.search(r'<pubDate>(.*?)</pubDate>', entry)
                            
                            if title_match and link_match:
                                title = title_match.group(1).strip()
                                # Filter by query if provided
                                if not query or query.lower() in title.lower():
                                    results.append({
                                        "type": "article",
                                        "title": title,
                                        "url": link_match.group(1).strip(),
                                        "description": description_match.group(1).strip() if description_match else "",
                                        "published": pub_date_match.group(1).strip() if pub_date_match else "",
                                        "source": "medium"
                                    })
                        
                        # Cache the results
                        await self.cache_service.set("medium_data", query, results, max_results=max_results)
                        
                        logger.info(f"Collected {len(results)} Medium results for query: {query}")
                        return results
                    else:
                        logger.warning(f"Medium RSS error: {resp.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error collecting Medium data: {e}")
            return []
    
    async def collect_all_data(self, query: str, max_results: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        """Collect data from all sources in parallel"""
        try:
            # Collect from all sources concurrently
            tasks = [
                self.collect_github_data(query, max_results // 4),
                self.collect_stackoverflow_data(query, max_results // 4),
                self.collect_arxiv_data(query, max_results // 4),
                self.collect_medium_data(query, max_results // 4)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            combined_data = {
                "github": results[0] if not isinstance(results[0], Exception) else [],
                "stackoverflow": results[1] if not isinstance(results[1], Exception) else [],
                "arxiv": results[2] if not isinstance(results[2], Exception) else [],
                "medium": results[3] if not isinstance(results[3], Exception) else []
            }
            
            total_results = sum(len(data) for data in combined_data.values())
            logger.info(f"Collected {total_results} total results from all sources for query: {query}")
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error collecting all data: {e}")
            return {
                "github": [],
                "stackoverflow": [],
                "arxiv": [],
                "medium": []
            }
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get data collection statistics"""
        cache_stats = await self.cache_service.get_cache_stats()
        
        return {
            "cache_stats": cache_stats,
            "sources": ["github", "stackoverflow", "arxiv", "medium"],
            "rate_limits": {
                "github": "5000 requests/hour (authenticated)",
                "stackoverflow": "10000 requests/day",
                "arxiv": "No rate limit",
                "medium": "No rate limit"
            }
        } 