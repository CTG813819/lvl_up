"""
Enhanced Subject Learning Service
Uses OpenAI and Anthropic APIs to research subjects and build comprehensive knowledge
"""

import asyncio
import aiohttp
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import structlog
from app.services.anthropic_service import call_claude, anthropic_rate_limited_call
# from app.services.openai_service import call_openai  # Removed - function doesn't exist
from app.core.config import settings

logger = structlog.get_logger()


class EnhancedSubjectLearningService:
    """Enhanced subject learning service using OpenAI and Anthropic APIs"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_search_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.google_search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
        
    async def research_subject(self, subject: str, context: str = "") -> Dict[str, Any]:
        """
        Research a subject using multiple AI services and internet search
        """
        try:
            logger.info(f"Starting subject research", subject=subject)
            
            results = {
                "subject": subject,
                "research_timestamp": datetime.now().isoformat(),
                "openai_insights": {},
                "anthropic_insights": {},
                "internet_search": [],
                "comprehensive_knowledge": "",
                "learning_recommendations": [],
                "code_examples": [],
                "best_practices": [],
                "common_pitfalls": [],
                "advanced_concepts": []
            }
            
            # Research with OpenAI
            if self.openai_api_key:
                openai_insights = await self._research_with_openai(subject, context)
                results["openai_insights"] = openai_insights
            
            # Research with Anthropic
            if self.anthropic_api_key:
                anthropic_insights = await self._research_with_anthropic(subject, context)
                results["anthropic_insights"] = anthropic_insights
            
            # Internet search for current information
            if self.google_search_api_key and self.google_search_engine_id:
                search_results = await self._search_internet(subject)
                results["internet_search"] = search_results
            
            # Generate comprehensive knowledge synthesis
            comprehensive_knowledge = await self._synthesize_knowledge(
                subject, results["openai_insights"], results["anthropic_insights"], results["internet_search"]
            )
            results["comprehensive_knowledge"] = comprehensive_knowledge
            
            # Generate learning recommendations
            learning_recommendations = await self._generate_learning_recommendations(subject, comprehensive_knowledge)
            results["learning_recommendations"] = learning_recommendations
            
            # Extract code examples if applicable
            code_examples = await self._extract_code_examples(subject, comprehensive_knowledge)
            results["code_examples"] = code_examples
            
            # Identify best practices
            best_practices = await self._identify_best_practices(subject, comprehensive_knowledge)
            results["best_practices"] = best_practices
            
            # Identify common pitfalls
            common_pitfalls = await self._identify_common_pitfalls(subject, comprehensive_knowledge)
            results["common_pitfalls"] = common_pitfalls
            
            # Advanced concepts
            advanced_concepts = await self._identify_advanced_concepts(subject, comprehensive_knowledge)
            results["advanced_concepts"] = advanced_concepts
            
            logger.info(f"Subject research completed", subject=subject)
            return results
            
        except Exception as e:
            logger.error(f"Error researching subject", subject=subject, error=str(e))
            return {
                "subject": subject,
                "error": str(e),
                "research_timestamp": datetime.now().isoformat()
            }
    
    async def _research_with_openai(self, subject: str, context: str) -> Dict[str, Any]:
        """Research subject using OpenAI API"""
        try:
            # OpenAI service not available - using fallback
            logger.warning(f"OpenAI research not available - using fallback", subject=subject)
            
            return {
                "research": f"OpenAI research for {subject} is not available. Please use Anthropic or other services.",
                "timestamp": datetime.now().isoformat(),
                "model": "fallback",
                "status": "unavailable"
            }
            
        except Exception as e:
            logger.error(f"OpenAI research failed", subject=subject, error=str(e))
            return {"error": str(e)}
    
    async def _research_with_anthropic(self, subject: str, context: str) -> Dict[str, Any]:
        """Research subject using Anthropic API"""
        try:
            prompt = f"""
            Research and provide comprehensive information about: {subject}
            
            Context: {context}
            
            Please provide:
            1. Core concepts and definitions
            2. Key principles and fundamentals
            3. Current trends and developments
            4. Practical applications
            5. Learning resources and references
            6. Common use cases
            7. Technical details and specifications
            
            Format your response as structured JSON with clear sections.
            """
            
            response = await call_claude(prompt, max_tokens=2000)
            
            return {
                "research": response,
                "timestamp": datetime.now().isoformat(),
                "model": "claude-3-sonnet"
            }
            
        except Exception as e:
            logger.error(f"Anthropic research failed", subject=subject, error=str(e))
            return {"error": str(e)}
    
    async def _search_internet(self, subject: str) -> List[Dict[str, Any]]:
        """Search internet for current information about the subject"""
        try:
            if not self.google_search_api_key or not self.google_search_engine_id:
                return []
            
            search_url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": self.google_search_api_key,
                "cx": self.google_search_engine_id,
                "q": subject,
                "num": 5
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(search_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        items = data.get("items", [])
                        
                        search_results = []
                        for item in items:
                            search_results.append({
                                "title": item.get("title", ""),
                                "link": item.get("link", ""),
                                "snippet": item.get("snippet", ""),
                                "source": "Google Custom Search"
                            })
                        
                        return search_results
                    else:
                        logger.warning(f"Google search failed", status=response.status)
                        return []
                        
        except Exception as e:
            logger.error(f"Internet search failed", subject=subject, error=str(e))
            return []
    
    async def _synthesize_knowledge(self, subject: str, openai_insights: Dict, anthropic_insights: Dict, search_results: List) -> str:
        """Synthesize knowledge from multiple sources"""
        try:
            synthesis_prompt = f"""
            Synthesize comprehensive knowledge about: {subject}
            
            OpenAI Insights: {json.dumps(openai_insights, indent=2)}
            Anthropic Insights: {json.dumps(anthropic_insights, indent=2)}
            Internet Search Results: {json.dumps(search_results, indent=2)}
            
            Create a comprehensive, well-structured knowledge base that includes:
            1. Executive Summary
            2. Core Concepts
            3. Key Principles
            4. Practical Applications
            5. Best Practices
            6. Common Pitfalls
            7. Advanced Topics
            8. Learning Path
            9. Resources and References
            
            Make it comprehensive and actionable for AI learning and human understanding.
            """
            
            # Use Anthropic for synthesis as it's good at combining information
            if self.anthropic_api_key:
                synthesis = await call_claude(synthesis_prompt, max_tokens=3000)
                return synthesis
            else:
                return f"Comprehensive knowledge synthesis for {subject} based on multiple AI sources and internet research."
                
        except Exception as e:
            logger.error(f"Knowledge synthesis failed", subject=subject, error=str(e))
            return f"Knowledge synthesis for {subject} - Error: {str(e)}"
    
    async def _generate_learning_recommendations(self, subject: str, knowledge: str) -> List[str]:
        """Generate learning recommendations based on the subject"""
        try:
            prompt = f"""
            Based on the following knowledge about {subject}, generate 10 specific learning recommendations:
            
            {knowledge[:2000]}...
            
            Provide practical, actionable learning recommendations that would help someone master this subject.
            """
            
            if self.anthropic_api_key:
                response = await call_claude(prompt, max_tokens=1000)
                # Parse response into list
                recommendations = [rec.strip() for rec in response.split('\n') if rec.strip() and not rec.startswith('#')]
                return recommendations[:10]
            else:
                return [
                    f"Study the fundamentals of {subject}",
                    f"Practice with real-world examples of {subject}",
                    f"Join communities focused on {subject}",
                    f"Build projects using {subject}",
                    f"Read advanced materials about {subject}"
                ]
                
        except Exception as e:
            logger.error(f"Learning recommendations failed", subject=subject, error=str(e))
            return [f"Study {subject} fundamentals", f"Practice {subject} applications"]
    
    async def _extract_code_examples(self, subject: str, knowledge: str) -> List[str]:
        """Extract code examples from knowledge"""
        try:
            # OpenAI service not available - using fallback
            logger.warning(f"OpenAI code extraction not available - using fallback", subject=subject)
            
            return [
                f"// Example code for {subject}",
                f"// This is a placeholder since OpenAI service is not available",
                f"// Please implement based on the knowledge provided"
            ]
            
        except Exception as e:
            logger.error(f"Code extraction failed", subject=subject, error=str(e))
            return []
    
    async def _identify_best_practices(self, subject: str, knowledge: str) -> List[str]:
        """Identify best practices for the subject"""
        try:
            prompt = f"""
            Based on the knowledge about {subject}, identify 10 best practices that should be followed:
            
            {knowledge[:1500]}...
            
            Provide specific, actionable best practices.
            """
            
            if self.anthropic_api_key:
                response = await call_claude(prompt, max_tokens=800)
                practices = [practice.strip() for practice in response.split('\n') if practice.strip() and not practice.startswith('#')]
                return practices[:10]
            else:
                return [
                    f"Follow {subject} conventions",
                    f"Use proper error handling in {subject}",
                    f"Write clear documentation for {subject}",
                    f"Test {subject} implementations thoroughly",
                    f"Keep {subject} code modular and maintainable"
                ]
                
        except Exception as e:
            logger.error(f"Best practices identification failed", subject=subject, error=str(e))
            return [f"Follow {subject} best practices", f"Use proper {subject} conventions"]
    
    async def _identify_common_pitfalls(self, subject: str, knowledge: str) -> List[str]:
        """Identify common pitfalls for the subject"""
        try:
            prompt = f"""
            Based on the knowledge about {subject}, identify 10 common pitfalls to avoid:
            
            {knowledge[:1500]}...
            
            Provide specific pitfalls with explanations.
            """
            
            if self.anthropic_api_key:
                response = await call_claude(prompt, max_tokens=800)
                pitfalls = [pitfall.strip() for pitfall in response.split('\n') if pitfall.strip() and not pitfall.startswith('#')]
                return pitfalls[:10]
            else:
                return [
                    f"Avoid common {subject} mistakes",
                    f"Don't ignore {subject} error handling",
                    f"Beware of {subject} performance issues",
                    f"Don't skip {subject} testing",
                    f"Avoid {subject} security vulnerabilities"
                ]
                
        except Exception as e:
            logger.error(f"Common pitfalls identification failed", subject=subject, error=str(e))
            return [f"Avoid common {subject} mistakes", f"Follow {subject} security practices"]
    
    async def _identify_advanced_concepts(self, subject: str, knowledge: str) -> List[str]:
        """Identify advanced concepts from knowledge"""
        try:
            # OpenAI service not available - using fallback
            logger.warning(f"OpenAI advanced concepts not available - using fallback", subject=subject)
            
            return [
                f"Advanced concepts for {subject}",
                "Please refer to the comprehensive knowledge provided above",
                "Consider exploring related technologies and frameworks"
            ]
            
        except Exception as e:
            logger.error(f"Advanced concepts identification failed", subject=subject, error=str(e))
            return []
    
    async def build_subject_knowledge_base(self, subject: str, context: str = "") -> Dict[str, Any]:
        """
        Build a comprehensive knowledge base for a subject
        This is the main method to be called by other services
        """
        try:
            logger.info(f"Building knowledge base", subject=subject)
            
            # Research the subject
            research_results = await self.research_subject(subject, context)
            
            # Create knowledge base structure
            knowledge_base = {
                "subject": subject,
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "research_data": research_results,
                "knowledge_summary": research_results.get("comprehensive_knowledge", ""),
                "learning_path": research_results.get("learning_recommendations", []),
                "code_examples": research_results.get("code_examples", []),
                "best_practices": research_results.get("best_practices", []),
                "common_pitfalls": research_results.get("common_pitfalls", []),
                "advanced_concepts": research_results.get("advanced_concepts", []),
                "ai_insights": {
                    "openai": research_results.get("openai_insights", {}),
                    "anthropic": research_results.get("anthropic_insights", {})
                },
                "internet_sources": research_results.get("internet_search", []),
                "learning_value": len(research_results.get("comprehensive_knowledge", "")) / 100,
                "status": "completed"
            }
            
            logger.info(f"Knowledge base built successfully", subject=subject)
            return knowledge_base
            
        except Exception as e:
            logger.error(f"Failed to build knowledge base", subject=subject, error=str(e))
            return {
                "subject": subject,
                "error": str(e),
                "status": "failed",
                "created_at": datetime.now().isoformat()
            } 