"""
Analysis Service - Claude for Data Analysis Only
Uses Claude only for analyzing collected data, not for data collection
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import structlog

from .cache_service import CacheService
from .data_collection_service import DataCollectionService
from app.services.anthropic_service import anthropic_rate_limited_call

logger = structlog.get_logger()

class AnalysisService:
    """Service for analyzing collected data using Claude"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AnalysisService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.cache_service = CacheService()
            self.data_collection_service = DataCollectionService()
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the analysis service"""
        instance = cls()
        await instance.cache_service.initialize()
        await instance.data_collection_service.initialize()
        logger.info("Analysis service initialized")
        return instance
    
    async def analyze_topic_with_data(self, topic: str, ai_name: str = "imperium") -> Dict[str, Any]:
        """Analyze a topic using collected data and Claude analysis"""
        try:
            logger.info(f"Starting analysis for topic: {topic}")
            
            # Step 1: Collect raw data from direct APIs (no Claude usage)
            logger.info(f"Collecting raw data for topic: {topic}")
            raw_data = await self.data_collection_service.collect_all_data(topic, max_results=20)
            
            # Step 2: Check if we have cached analysis
            cached_analysis = await self.cache_service.get("claude_analysis", topic, ai_name=ai_name)
            if cached_analysis:
                logger.info(f"Using cached analysis for topic: {topic}")
                return {
                    "topic": topic,
                    "raw_data": raw_data,
                    "analysis": cached_analysis,
                    "cached": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            # Step 3: Prepare data for Claude analysis
            analysis_prompt = self._create_analysis_prompt(topic, raw_data)
            
            # Step 4: Use Claude for analysis only (not data collection)
            logger.info(f"Requesting Claude analysis for topic: {topic}")
            claude_analysis = await anthropic_rate_limited_call(
                analysis_prompt,
                ai_name=ai_name,
                max_tokens=2000
            )
            
            # Step 5: Cache the analysis
            await self.cache_service.set("claude_analysis", topic, claude_analysis, ai_name=ai_name)
            
            return {
                "topic": topic,
                "raw_data": raw_data,
                "analysis": claude_analysis,
                "cached": False,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing topic {topic}: {e}")
            return {
                "topic": topic,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _create_analysis_prompt(self, topic: str, raw_data: Dict[str, List[Dict[str, Any]]]) -> str:
        """Create a prompt for Claude to analyze the collected data"""
        
        # Format the raw data for analysis
        data_summary = []
        total_items = 0
        
        for source, items in raw_data.items():
            if items:
                data_summary.append(f"{source.upper()} ({len(items)} items):")
                for item in items[:3]:  # Show first 3 items per source
                    title = item.get("title", "No title")
                    url = item.get("url", "No URL")
                    data_summary.append(f"  - {title} ({url})")
                data_summary.append("")
                total_items += len(items)
        
        prompt = f"""
You are an AI analyst tasked with analyzing collected data about: {topic}

RAW DATA COLLECTED ({total_items} total items):
{chr(10).join(data_summary)}

Please provide a comprehensive analysis including:

1. KEY INSIGHTS: What are the main patterns, trends, or insights from this data?
2. RELEVANCE ASSESSMENT: How relevant is this data to the topic "{topic}"?
3. QUALITY EVALUATION: Which sources provided the most valuable information?
4. GAPS IDENTIFIED: What important aspects of "{topic}" are missing from this data?
5. RECOMMENDATIONS: What should be the next steps for learning about "{topic}"?
6. ACTIONABLE INSIGHTS: What specific actions or experiments could be derived from this analysis?

Focus on providing actionable insights that can be used for AI learning and improvement.
Be concise but thorough in your analysis.
"""
        
        return prompt
    
    async def analyze_code_improvements(self, code_before: str, code_after: str, context: str = "") -> Dict[str, Any]:
        """Analyze code improvements using Claude"""
        try:
            # Check cache first
            cache_key = f"{hash(code_before + code_after + context)}"
            cached_analysis = await self.cache_service.get("code_analysis", cache_key)
            if cached_analysis:
                return cached_analysis
            
            # Create analysis prompt
            prompt = f"""
Analyze the following code improvement:

CONTEXT: {context}

CODE BEFORE:
{code_before}

CODE AFTER:
{code_after}

Please provide a detailed analysis including:

1. IMPROVEMENT QUALITY: Rate the improvement from 1-10 and explain why
2. TECHNICAL ASSESSMENT: What specific improvements were made?
3. BEST PRACTICES: Does the improved code follow better practices?
4. POTENTIAL ISSUES: Are there any concerns with the changes?
5. FURTHER SUGGESTIONS: What additional improvements could be made?
6. LEARNING VALUE: What can be learned from this improvement?

Provide specific, actionable feedback.
"""
            
            # Use Claude for analysis
            analysis = await anthropic_rate_limited_call(prompt, ai_name="guardian", max_tokens=1500)
            
            # Cache the analysis
            await self.cache_service.set("code_analysis", cache_key, analysis)
            
            return {
                "analysis": analysis,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing code improvements: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def analyze_learning_patterns(self, learning_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze learning patterns using Claude"""
        try:
            # Check cache first
            data_hash = hash(json.dumps(learning_data, sort_keys=True))
            cached_analysis = await self.cache_service.get("learning_analysis", str(data_hash))
            if cached_analysis:
                return cached_analysis
            
            # Prepare learning data summary
            success_count = sum(1 for item in learning_data if item.get("outcome") == "success")
            failure_count = sum(1 for item in learning_data if item.get("outcome") == "failure")
            total_count = len(learning_data)
            
            # Create analysis prompt
            success_rate = (success_count/total_count*100) if total_count > 0 else 0
            prompt = f"""
Analyze the following AI learning patterns:

LEARNING DATA SUMMARY:
- Total learning cycles: {total_count}
- Successful outcomes: {success_count}
- Failed outcomes: {failure_count}
- Success rate: {success_rate:.1f}%

RECENT LEARNING CYCLES (last 10):
{chr(10).join([f"- {item.get('ai_type', 'unknown')}: {item.get('outcome', 'unknown')} - {item.get('topic', 'unknown')}" for item in learning_data[-10:]])}

Please provide an analysis including:

1. SUCCESS PATTERNS: What patterns lead to successful learning?
2. FAILURE PATTERNS: What common causes of learning failures?
3. IMPROVEMENT OPPORTUNITIES: How can the learning process be improved?
4. AGENT PERFORMANCE: Which AI agents are performing best/worst?
5. TOPIC EFFECTIVENESS: Which topics lead to better learning outcomes?
6. RECOMMENDATIONS: Specific actions to improve learning effectiveness

Focus on actionable insights for improving the AI learning system.
"""
            
            # Use Claude for analysis
            analysis = await anthropic_rate_limited_call(prompt, ai_name="imperium", max_tokens=2000)
            
            # Cache the analysis
            await self.cache_service.set("learning_analysis", str(data_hash), analysis)
            
            return {
                "analysis": analysis,
                "statistics": {
                    "total_cycles": total_count,
                    "success_count": success_count,
                    "failure_count": failure_count,
                    "success_rate": (success_count/total_count*100) if total_count > 0 else 0
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing learning patterns: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis service statistics"""
        cache_stats = await self.cache_service.get_cache_stats()
        
        return {
            "cache_stats": cache_stats,
            "analysis_types": [
                "topic_analysis",
                "code_improvement_analysis", 
                "learning_pattern_analysis"
            ],
            "claude_usage": "analysis_only",
            "data_collection": "direct_apis"
        } 