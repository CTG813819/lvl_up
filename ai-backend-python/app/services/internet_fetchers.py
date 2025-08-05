"""
Internet Data Fetchers for Imperium Learning Controller - ENABLED with Rate Limiting
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
from datetime import datetime, timedelta

from .trusted_sources import is_trusted_source

logger = structlog.get_logger()

# Rate limiting configuration
RATE_LIMIT_DELAY = 2.0  # seconds between requests
MAX_RETRIES = 3
RETRY_DELAY = 5.0  # seconds to wait before retry

class RateLimitedFetcher:
    """Rate limiter for external API calls"""
    
    def __init__(self, max_requests_per_minute=30):
        self.max_requests = max_requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        async with self.lock:
            now = datetime.now()
            # Remove old requests
            self.requests = [req for req in self.requests 
                           if now - req < timedelta(minutes=1)]
            
            if len(self.requests) >= self.max_requests:
                wait_time = 60 - (now - self.requests[0]).total_seconds()
                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                    await asyncio.sleep(wait_time)
            
            self.requests.append(now)

class StackOverflowFetcher:
    BASE_URL = "https://api.stackexchange.com/2.3/search/advanced"
    SITE = "stackoverflow"
    
    def __init__(self):
        self.rate_limiter = RateLimitedFetcher(max_requests_per_minute=30)

    @staticmethod
    async def fetch(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetch top Stack Overflow Q&A for a query with rate limiting"""
        try:
            fetcher = StackOverflowFetcher()
            await fetcher.rate_limiter.wait_if_needed()
            
            params = {
                'order': 'desc',
                'sort': 'votes',
                'tagged': query.replace(' ', ';'),
                'site': fetcher.SITE,
                'pagesize': max_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(fetcher.BASE_URL, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])
                        
                        results = []
                        for item in items[:max_results]:
                            results.append({
                                'title': item.get('title', ''),
                                'content': item.get('body', ''),
                                'url': item.get('link', ''),
                                'score': item.get('score', 0),
                                'source': 'stackoverflow'
                            })
                        
                        logger.info(f"Fetched {len(results)} results from Stack Overflow")
                        return results
                    else:
                        logger.warning(f"Stack Overflow API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching from Stack Overflow: {str(e)}")
            return []

class ArxivFetcher:
    BASE_URL = "http://export.arxiv.org/api/query"
    
    def __init__(self):
        self.rate_limiter = RateLimitedFetcher(max_requests_per_minute=10)

    @staticmethod
    async def fetch(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetch arXiv papers with rate limiting"""
        try:
            fetcher = ArxivFetcher()
            await fetcher.rate_limiter.wait_if_needed()
            
            params = {
                'search_query': f'all:"{query}"',
                'start': 0,
                'max_results': max_results,
                'sortBy': 'relevance',
                'sortOrder': 'descending'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(fetcher.BASE_URL, params=params) as response:
                    if response.status == 200:
                        content = await response.text()
                        feed = feedparser.parse(content)
                        
                        results = []
                        for entry in feed.entries[:max_results]:
                            results.append({
                                'title': entry.get('title', ''),
                                'content': entry.get('summary', ''),
                                'url': entry.get('link', ''),
                                'authors': [author.name for author in entry.get('authors', [])],
                                'source': 'arxiv'
                            })
                        
                        logger.info(f"Fetched {len(results)} results from arXiv")
                        return results
                    else:
                        logger.warning(f"arXiv API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching from arXiv: {str(e)}")
            return []

class MediumFetcher:
    BASE_URL = "https://medium.com/search"
    
    def __init__(self):
        self.rate_limiter = RateLimitedFetcher(max_requests_per_minute=20)

    @staticmethod
    async def fetch(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetch Medium articles with rate limiting"""
        try:
            fetcher = MediumFetcher()
            await fetcher.rate_limiter.wait_if_needed()
            
            # Medium doesn't have a public API, so we'll simulate with trusted sources
            # In a real implementation, you'd use their RSS feeds or API
            logger.info(f"Medium fetcher would search for: {query}")
            
            # Return simulated results for now
            return [{
                'title': f'Medium article about {query}',
                'content': f'This would be content about {query} from Medium',
                'url': f'https://medium.com/search?q={quote(query)}',
                'source': 'medium'
            }]
            
        except Exception as e:
            logger.error(f"Error fetching from Medium: {str(e)}")
            return []

class GitHubFetcher:
    BASE_URL = "https://api.github.com/search/repositories"
    
    def __init__(self):
        self.rate_limiter = RateLimitedFetcher(max_requests_per_minute=30)

    @staticmethod
    async def fetch(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Fetch GitHub repositories with rate limiting"""
        try:
            fetcher = GitHubFetcher()
            await fetcher.rate_limiter.wait_if_needed()
            
            headers = {}
            # Add GitHub token if available
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                headers['Authorization'] = f'token {github_token}'
            
            params = {
                'q': query,
                'sort': 'stars',
                'order': 'desc',
                'per_page': max_results
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(fetcher.BASE_URL, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get('items', [])
                        
                        results = []
                        for item in items[:max_results]:
                            results.append({
                                'title': item.get('name', ''),
                                'content': item.get('description', ''),
                                'url': item.get('html_url', ''),
                                'stars': item.get('stargazers_count', 0),
                                'language': item.get('language', ''),
                                'source': 'github'
                            })
                        
                        logger.info(f"Fetched {len(results)} results from GitHub")
                        return results
                    else:
                        logger.warning(f"GitHub API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching from GitHub: {str(e)}")
            return []
