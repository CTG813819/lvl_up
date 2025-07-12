"""
Internet Data Fetchers for Imperium Learning Controller - DISABLED
Fetches knowledge from trusted sources (Stack Overflow, GitHub, arXiv, Medium, etc.)
"""

import aiohttp
import asyncio
from typing import List, Dict, Any
from urllib.parse import quote
import os
import feedparser
import time
import structlog

from .trusted_sources import is_trusted_source

logger = structlog.get_logger()

# Rate limiting configuration
RATE_LIMIT_DELAY = 2.0  # seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 5.0  # seconds to wait before retry

class StackOverflowFetcher:
    BASE_URL = "https://api.stackexchange.com/2.3/search/advanced"
    SITE = "stackoverflow"

    @staticmethod
    async def fetch(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetch top Stack Overflow Q&A for a query - DISABLED to prevent rate limiting"""
        logger.warning("StackOverflow fetcher DISABLED to prevent rate limiting")
        return []

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

class GitHubFetcher:
    BASE_URL = "https://api.github.com/search/repositories"

    @staticmethod
    async def fetch(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetch GitHub repositories with rate limiting and error handling"""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if GITHUB_TOKEN:
            headers["Authorization"] = f"token {GITHUB_TOKEN}"
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": max_results}
        url = f"{GitHubFetcher.BASE_URL}?" + "&".join(f"{k}={quote(str(v))}" for k, v in params.items())
        
        for attempt in range(MAX_RETRIES):
            try:
                # Rate limiting delay
                if attempt > 0:
                    await asyncio.sleep(RATE_LIMIT_DELAY)
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as resp:
                        if resp.status == 403:  # GitHub rate limit
                            logger.warning(f"Rate limited by GitHub API, attempt {attempt + 1}/{MAX_RETRIES}")
                            if attempt < MAX_RETRIES - 1:
                                await asyncio.sleep(RETRY_DELAY * (attempt + 1))
                                continue
                            else:
                                logger.error("Max retries reached for GitHub API")
                                return []
                        
                        if resp.status != 200:
                            logger.error(f"GitHub API error: {resp.status}")
                            return []
                        
                        data = await resp.json()
                        results = []
                        for item in data.get("items", []):
                            html_url = item.get("html_url", "")
                            if is_trusted_source(html_url):
                                results.append({
                                    "title": item.get("full_name"),
                                    "url": html_url,
                                    "summary": item.get("description", ""),
                                    "stars": item.get("stargazers_count", 0),
                                    "language": item.get("language", ""),
                                    "source": "github"
                                })
                        return results
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout fetching from GitHub, attempt {attempt + 1}/{MAX_RETRIES}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                else:
                    logger.error("Max retries reached for GitHub API timeout")
                    return []
                    
            except Exception as e:
                logger.error(f"Error fetching from GitHub: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(RETRY_DELAY)
                    continue
                else:
                    return []
        
        return []

class ArxivFetcher:
    BASE_URL = "http://export.arxiv.org/api/query"

    @staticmethod
    async def fetch(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetch arXiv papers - DISABLED to prevent external API issues"""
        logger.warning("Arxiv fetcher DISABLED to prevent external API issues")
        return []

class MediumFetcher:
    # Uses RSS feeds for Medium and Dev.to
    FEEDS = [
        "https://medium.com/feed/tag/flutter",
        "https://dev.to/feed/tag/flutter"
    ]

    @staticmethod
    async def fetch(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetch Medium articles - DISABLED to prevent external API issues"""
        logger.warning("Medium fetcher DISABLED to prevent external API issues")
        return [] 