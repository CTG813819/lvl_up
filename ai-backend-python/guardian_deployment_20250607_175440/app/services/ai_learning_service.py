"""
AI Learning Service with scikit-learn integration
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import structlog
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import requests

from ..core.database import get_session
from ..core.config import settings
from .ml_service import MLService

logger = structlog.get_logger()


class AILearningService:
    """AI Learning service with ML integration"""
    
    _instance = None
    _initialized = False
    _learning_states = {}
    _periodic_task_running = False
    _last_periodic_learning = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AILearningService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.ml_service = MLService()
            self._initialized = True
    
    @classmethod
    async def initialize(cls):
        """Initialize the AI Learning service"""
        instance = cls()
        await instance._start_periodic_internet_learning()
        logger.info("AI Learning Service initialized with periodic internet learning")
    
    async def _start_periodic_internet_learning(self):
        """Start periodic internet learning every 60 minutes"""
        if self._periodic_task_running:
            return
        
        self._periodic_task_running = True
        
        async def periodic_learning_loop():
            while self._periodic_task_running:
                try:
                    logger.info("🔄 Starting periodic internet learning cycle for all AIs")
                    
                    # Perform internet-augmented learning for all AIs
                    learning_results = await self._perform_periodic_internet_learning()
                    
                    # Log results
                    self._last_periodic_learning = datetime.now()
                    logger.info("✅ Periodic internet learning completed", 
                               results=learning_results,
                               timestamp=self._last_periodic_learning.isoformat())
                    
                    # Send notification (can be extended to frontend)
                    await self._send_learning_notification(learning_results)
                    
                except Exception as e:
                    logger.error("❌ Error in periodic internet learning", error=str(e))
                
                # Wait 60 minutes (3600 seconds)
                await asyncio.sleep(1200)  # Wait 20 minutes (1200 seconds)
        
        # Start the periodic task in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        asyncio.create_task(periodic_learning_loop())
    
    async def _perform_periodic_internet_learning(self) -> Dict[str, Any]:
        """Perform periodic internet-augmented learning for all AIs"""
        start_time = time.time()
        results = {
            "timestamp": datetime.now().isoformat(),
            "ai_learning_results": {},
            "total_learning_value": 0.0,
            "search_results_count": 0,
            "processing_time": 0
        }
        
        # Define learning topics for each AI
        learning_topics = {
            "imperium": [
                "system architecture patterns",
                "strategic planning methodologies",
                "complex problem solving techniques",
                "enterprise software design",
                "scalability best practices",
                "machine learning fundamentals",
                "deep learning architectures",
                "AI model deployment",
                "data science workflows",
                "reinforcement learning",
                "natural language processing",
                "computer vision",
                "microservices architecture",
                "API security best practices",
                "database optimization (SQL/NoSQL)",
                "asynchronous programming in Python",
                "DevOps and CI/CD pipelines",
                "cloud-native design patterns",
                "RESTful API design",
                "GraphQL APIs",
                "distributed systems",
                "observability and monitoring",
                "error handling and resilience",
                "scalability and load balancing",
                "containerization (Docker, Kubernetes)",
                "automated testing strategies",
                "code review and static analysis"
            ],
            "guardian": [
                "security best practices",
                "code quality standards",
                "testing methodologies",
                "performance optimization",
                "code review techniques"
            ],
            "sandbox": [
                "experimental programming",
                "rapid prototyping",
                "creative problem solving",
                "new technology trends",
                "innovation methodologies"
            ],
            "conquest": [
                "app development frameworks",
                "mobile app design patterns",
                "user experience design",
                "app store optimization",
                "cross-platform development"
            ]
        }
        
        total_learning_value = 0.0
        total_search_results = 0
        
        # Process each AI
        for ai_type, topics in learning_topics.items():
            ai_results = {
                "topics_learned": [],
                "learning_score": 0.0,
                "search_results": [],
                "insights_gained": []
            }
            
            # Learn from each topic with internet search
            for topic in topics[:2]:  # Limit to 2 topics per AI per cycle
                try:
                    # Perform internet search for the topic
                    search_results = await self._search_internet(topic, [ai_type], [topic])
                    total_search_results += len(search_results)
                    
                    # Simulate AI learning with internet data
                    ai_response = await self._simulate_ai_learning(
                        ai_type=ai_type,
                        subject=topic,
                        description=f"Periodic learning about {topic}",
                        code=None,
                        tags=[ai_type, "periodic_learning"],
                        keywords=[topic],
                        search_results=search_results,
                        weight=1.0
                    )
                    
                    ai_results["topics_learned"].append(topic)
                    ai_results["learning_score"] += ai_response.get("learning_score", 0.0)
                    ai_results["search_results"].extend(search_results)
                    ai_results["insights_gained"].append(ai_response.get("insights", ""))
                    
                except Exception as e:
                    logger.error(f"Error learning topic {topic} for {ai_type}", error=str(e))
            
            # Calculate average learning score for this AI
            if ai_results["topics_learned"]:
                ai_results["learning_score"] = ai_results["learning_score"] / len(ai_results["topics_learned"])
                total_learning_value += ai_results["learning_score"]
            
            results["ai_learning_results"][ai_type.title()] = ai_results
        
        # Calculate overall metrics
        results["total_learning_value"] = total_learning_value / len(learning_topics) if learning_topics else 0.0
        results["search_results_count"] = total_search_results
        results["processing_time"] = time.time() - start_time
        
        return results
    
    async def _send_learning_notification(self, learning_results: Dict[str, Any]):
        """Send notification about completed learning cycle"""
        try:
            # Log detailed notification
            notification = {
                "type": "periodic_learning_completed",
                "timestamp": learning_results["timestamp"],
                "message": f"Periodic internet learning completed for all AIs",
                "summary": {
                    "total_learning_value": round(learning_results["total_learning_value"], 3),
                    "search_results": learning_results["search_results_count"],
                    "processing_time": round(learning_results["processing_time"], 2),
                    "ais_updated": list(learning_results["ai_learning_results"].keys())
                }
            }
            
            logger.info("📢 Learning notification sent", notification=notification)
            
            # Here you can extend to send to frontend via WebSocket, database, etc.
            # For now, we'll just log it
            
        except Exception as e:
            logger.error("Error sending learning notification", error=str(e))
    
    def get_last_periodic_learning_info(self) -> Dict[str, Any]:
        """Get information about the last periodic learning cycle"""
        return {
            "last_learning_time": self._last_periodic_learning.isoformat() if self._last_periodic_learning else None,
            "is_periodic_learning_active": self._periodic_task_running,
            "next_learning_in_minutes": self._get_next_learning_countdown()
        }
    
    def _get_next_learning_countdown(self) -> Optional[int]:
        """Calculate minutes until next learning cycle"""
        if not self._last_periodic_learning:
            return None
        
        next_learning = self._last_periodic_learning + timedelta(hours=1)
        now = datetime.now()
        
        if next_learning > now:
            return int((next_learning - now).total_seconds() / 60)
        else:
            return 0  # Due now
    
    async def process_enhanced_oath_paper(
        self,
        oath_paper_id: str,
        subject: str,
        tags: List[str],
        description: Optional[str] = None,
        code: Optional[str] = None,
        target_ai: Optional[str] = None,
        ai_weights: Optional[Dict[str, float]] = None,
        extract_keywords: bool = True,
        internet_search: bool = True,  # Always enabled for enhanced learning
        git_integration: bool = True,
        learning_instructions: Optional[Dict[str, bool]] = None
    ) -> Dict[str, Any]:
        """Process enhanced oath paper with advanced learning capabilities"""
        start_time = time.time()
        
        try:
            logger.info("Processing enhanced oath paper", 
                       oath_paper_id=oath_paper_id,
                       subject=subject,
                       target_ai=target_ai)
            
            # Initialize result structure
            result = {
                "ai_insights": {},
                "learning_value": 0.0,
                "ai_responses": {},
                "improvement_suggestions": "",
                "processing_time": 0,
                "keywords_extracted": [],
                "search_results": [],
                "git_operations": []
            }
            
            # Extract keywords if enabled
            if extract_keywords:
                keywords = await self._extract_keywords(subject, description, code, tags)
                result["keywords_extracted"] = keywords
                logger.info("Keywords extracted", keywords=keywords)
            
            # Perform internet search if enabled
            if internet_search:
                search_results = await self._search_internet(subject, tags, keywords if extract_keywords else [])
                result["search_results"] = search_results
                logger.info("Internet search completed", results_count=len(search_results))
            
            # Process with AI learning
            ai_responses = {}
            learning_value = 0.0
            
            # Determine which AIs to process
            if target_ai and target_ai != "All AIs":
                ai_types = [target_ai.lower()]
            else:
                ai_types = ["imperium", "guardian", "sandbox", "conquest"]
            
            # Process each AI
            for ai_type in ai_types:
                ai_weight = ai_weights.get(ai_type.title(), 1.0) if ai_weights else 1.0
                
                # Simulate AI learning process
                ai_response = await self._simulate_ai_learning(
                    ai_type=ai_type,
                    subject=subject,
                    description=description,
                    code=code,
                    tags=tags,
                    keywords=result.get("keywords_extracted", []),
                    search_results=result.get("search_results", []),
                    weight=ai_weight
                )
                
                ai_responses[ai_type.title()] = ai_response
                learning_value += ai_response.get("learning_score", 0.0) * ai_weight
            
            # Calculate average learning value
            if ai_responses:
                learning_value = learning_value / len(ai_responses)
            
            # Generate improvement suggestions
            improvement_suggestions = await self._generate_improvement_suggestions(
                subject, description, code, tags, result.get("search_results", [])
            )
            
            # Git integration if enabled
            if git_integration:
                git_ops = await self._perform_git_operations(oath_paper_id, subject, description, code)
                result["git_operations"] = git_ops
            
            # Update result
            result.update({
                "ai_responses": ai_responses,
                "learning_value": learning_value,
                "improvement_suggestions": improvement_suggestions,
                "processing_time": time.time() - start_time
            })
            
            logger.info("Enhanced oath paper processing completed",
                       oath_paper_id=oath_paper_id,
                       processing_time=result["processing_time"],
                       learning_value=learning_value)
            
            return result
            
        except Exception as e:
            logger.error("Error processing enhanced oath paper", 
                        error=str(e),
                        oath_paper_id=oath_paper_id)
            return {
                "ai_insights": {},
                "learning_value": 0.0,
                "ai_responses": {},
                "improvement_suggestions": "",
                "processing_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def _extract_keywords(
        self, 
        subject: str, 
        description: Optional[str], 
        code: Optional[str], 
        tags: List[str]
    ) -> List[str]:
        """Extract keywords from oath paper content"""
        try:
            # Combine all text content
            text_content = f"{subject} {' '.join(tags)}"
            if description:
                text_content += f" {description}"
            if code:
                text_content += f" {code}"
            
            # Simple keyword extraction (in a real implementation, use NLP libraries)
            words = text_content.lower().split()
            # Remove common words and short words
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            keywords = [word for word in words if len(word) > 3 and word not in stop_words]
            
            # Add original tags
            keywords.extend(tags)
            
            # Remove duplicates and limit to top 10
            unique_keywords = list(set(keywords))[:10]
            
            return unique_keywords
            
        except Exception as e:
            logger.error("Error extracting keywords", error=str(e))
            return tags  # Fallback to original tags
    
    async def _search_internet(self, subject: str, tags: list, keywords: list) -> list:
        """Search internet for relevant information using real APIs (Stack Overflow, GitHub)"""
        results = []
        # Stack Overflow
        so_url = "https://api.stackexchange.com/2.3/search/advanced"
        so_params = {
            "order": "desc",
            "sort": "relevance",
            "q": subject,
            "site": "stackoverflow",
            "pagesize": 3,
        }
        if tags:
            so_params["tagged"] = ";".join(tags)
        try:
            so_resp = requests.get(so_url, params=so_params, timeout=5)
            if so_resp.status_code == 200:
                for item in so_resp.json().get("items", []):
                    results.append({
                        "title": item["title"],
                        "url": item["link"],
                        "snippet": item.get("excerpt", ""),
                        "source": "StackOverflow"
                    })
        except Exception as e:
            logger.error("Stack Overflow API error", error=str(e))
        # GitHub
        github_token = getattr(settings, "github_token", None)
        if github_token:
            gh_url = "https://api.github.com/search/code"
            gh_headers = {"Authorization": f"token {github_token}"}
            gh_params = {"q": f"{subject} language:python", "per_page": 3}
            try:
                gh_resp = requests.get(gh_url, headers=gh_headers, params=gh_params, timeout=5)
                if gh_resp.status_code == 200:
                    for item in gh_resp.json().get("items", []):
                        results.append({
                            "title": item["name"],
                            "url": item["html_url"],
                            "snippet": item.get("path", ""),
                            "source": "GitHub"
                        })
            except Exception as e:
                logger.error("GitHub API error", error=str(e))
        # Fallback: Simulated results if nothing found
        if not results:
            results.append({
                "title": f"Search result for {subject}",
                "url": f"https://example.com/search/{subject}",
                "snippet": f"Relevant information about {subject} from the internet",
                "source": "Simulated"
            })
        return results
    
    async def _simulate_ai_learning(
        self,
        ai_type: str,
        subject: str,
        description: Optional[str],
        code: Optional[str],
        tags: List[str],
        keywords: List[str],
        search_results: List[Dict[str, Any]],
        weight: float = 1.0
    ) -> Dict[str, Any]:
        """Simulate AI learning process"""
        try:
            # Simulate learning based on AI type
            learning_patterns = {
                "imperium": {
                    "focus": "strategic thinking and system design",
                    "learning_score": 0.9,
                    "capabilities": ["system_architecture", "strategic_planning", "complex_problem_solving"]
                },
                "guardian": {
                    "focus": "security and validation",
                    "learning_score": 0.8,
                    "capabilities": ["security_analysis", "input_validation", "error_handling"]
                },
                "sandbox": {
                    "focus": "experimentation and testing",
                    "learning_score": 0.7,
                    "capabilities": ["code_testing", "experimentation", "rapid_prototyping"]
                },
                "conquest": {
                    "focus": "app generation and deployment",
                    "learning_score": 0.85,
                    "capabilities": ["app_generation", "deployment", "user_experience"]
                }
            }
            
            pattern = learning_patterns.get(ai_type, {
                "focus": "general learning",
                "learning_score": 0.6,
                "capabilities": ["general_knowledge"]
            })
            
            # Adjust learning score based on content quality
            content_score = 0.5
            if description:
                content_score += 0.2
            if code:
                content_score += 0.3
            if keywords:
                content_score += 0.1
            
            final_score = pattern["learning_score"] * content_score * weight
            
            return {
                "ai_type": ai_type,
                "learning_score": final_score,
                "focus_area": pattern["focus"],
                "capabilities_learned": pattern["capabilities"],
                "content_quality": content_score,
                "learning_status": "completed"
            }
            
        except Exception as e:
            logger.error("Error simulating AI learning", error=str(e), ai_type=ai_type)
            return {
                "ai_type": ai_type,
                "learning_score": 0.0,
                "focus_area": "error",
                "capabilities_learned": [],
                "content_quality": 0.0,
                "learning_status": "failed"
            }
    
    async def _generate_improvement_suggestions(
        self,
        subject: str,
        description: Optional[str],
        code: Optional[str],
        tags: List[str],
        search_results: List[Dict[str, Any]]
    ) -> str:
        """Generate improvement suggestions based on content and search results"""
        try:
            suggestions = []
            
            # Content-based suggestions
            if not description:
                suggestions.append("Add a detailed description to improve learning value")
            
            if not code:
                suggestions.append("Include code examples for better practical learning")
            
            if len(tags) < 3:
                suggestions.append("Add more specific tags for better categorization")
            
            # Search-based suggestions
            if search_results:
                suggestions.append("Consider incorporating insights from recent research and best practices")
            
            # General suggestions
            suggestions.append("Review and refine the content for clarity and completeness")
            
            return "; ".join(suggestions)
            
        except Exception as e:
            logger.error("Error generating improvement suggestions", error=str(e))
            return "Review content for improvements"
    
    async def _perform_git_operations(
        self,
        oath_paper_id: str,
        subject: str,
        description: Optional[str],
        code: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Perform Git operations for oath paper"""
        try:
            # Simulate Git operations (in a real implementation, use Git APIs)
            operations = []
            
            # Simulate file creation
            operations.append({
                "operation": "create_file",
                "file": f"oath_papers/{oath_paper_id}.md",
                "status": "success"
            })
            
            # Simulate commit
            operations.append({
                "operation": "commit",
                "message": f"Add oath paper: {subject}",
                "status": "success"
            })
            
            # Simulate push
            operations.append({
                "operation": "push",
                "branch": "main",
                "status": "success"
            })
            
            return operations
            
        except Exception as e:
            logger.error("Error performing Git operations", error=str(e))
            return [{"operation": "error", "status": "failed", "error": str(e)}]

    async def learn_from_proposal(self, proposal_id: str, status: str, feedback_reason: str = None):
        """Learn from a proposal using ML analysis"""
        try:
            from sqlalchemy import select
            from ..models.sql_models import Proposal, Learning
            import uuid
            
            session = get_session()
            try:
                # Get proposal
                stmt = select(Proposal).where(Proposal.id == uuid.UUID(proposal_id))
                result = await session.execute(stmt)
                proposal_data = result.scalar_one_or_none()
                
                if not proposal_data:
                    logger.warning("Proposal not found for learning", proposal_id=proposal_id)
                    return
                
                # Update proposal with feedback
                proposal_data.status = status
                proposal_data.user_feedback = status if status in ["approved", "rejected"] else None
                proposal_data.user_feedback_reason = feedback_reason
                proposal_data.updated_at = datetime.utcnow()
                
                await session.commit()
                
                # Analyze proposal quality using ML
                ml_analysis = await self.ml_service.analyze_proposal_quality(proposal_data)
                
                # Store learning data
                learning_entry = Learning(
                    ai_type=proposal_data.ai_type,
                    learning_type="proposal_feedback",
                    pattern=status,
                    context=feedback_reason,
                    feedback=str(ml_analysis),
                    confidence=ml_analysis.get('quality_score', 0.5),
                    created_at=datetime.utcnow()
                )
                
                session.add(learning_entry)
                await session.commit()
                
                logger.info("Learning from proposal completed", 
                           proposal_id=proposal_id, 
                           status=status,
                           quality_score=ml_analysis.get('quality_score', 0))
                
            except Exception as e:
                logger.error("Error in proposal processing", error=str(e), proposal_id=proposal_id)
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error learning from proposal", error=str(e), proposal_id=proposal_id)
    
    async def get_learning_stats(self, ai_type: str) -> Dict[str, Any]:
        """Get learning statistics"""
        try:
            from sqlalchemy import select, desc
            from ..models.sql_models import Learning, Proposal
            
            session = get_session()
            try:
                # Get recent learning entries
                stmt = select(Learning).where(
                    Learning.ai_type == ai_type
                ).order_by(desc(Learning.created_at)).limit(100)
                
                result = await session.execute(stmt)
                recent_learning = result.scalars().all()
                
                # Get recent proposals for approval rate
                stmt = select(Proposal).where(
                    Proposal.ai_type == ai_type
                ).order_by(desc(Proposal.created_at)).limit(100)
                
                result = await session.execute(stmt)
                recent_proposals = result.scalars().all()
                
                stats = {
                    'total_learning_entries': len(recent_learning),
                    'recent_approval_rate': 0,
                    'average_quality_score': 0,
                    'learning_state': self._learning_states.get(ai_type, {'is_learning': False})
                }
                
                if recent_proposals:
                    # Calculate approval rate
                    approved = sum(1 for entry in recent_proposals if entry.user_feedback == 'approved')
                    stats['recent_approval_rate'] = approved / len(recent_proposals)
                
                if recent_learning:
                    # Calculate average quality score from learning entries
                    quality_scores = [entry.confidence for entry in recent_learning if entry.confidence]
                    if quality_scores:
                        stats['average_quality_score'] = sum(quality_scores) / len(quality_scores)
                
                return stats
                
            finally:
                await session.close()
            
        except Exception as e:
            logger.error("Error getting learning stats", error=str(e))
            return {}
    
    async def get_learning_insights(self, ai_type: str) -> Dict[str, Any]:
        """Get learning insights and recommendations"""
        try:
            # Get ML insights
            ml_insights = await self.ml_service.get_ml_insights()
            
            # Get learning stats
            stats = await self.get_learning_stats(ai_type)
            
            insights = {
                'ml_insights': ml_insights,
                'stats': stats,
                'recommendations': []
            }
            
            # Generate recommendations
            if stats.get('recent_approval_rate', 0) < 0.5:
                insights['recommendations'].append("Approval rate is low - consider improving proposal quality")
            
            if stats.get('average_quality_score', 0) < 0.6:
                insights['recommendations'].append("Average quality score is low - retrain ML models")
            
            return insights
            
        except Exception as e:
            logger.error("Error getting learning insights", error=str(e))
            return {} 
    
    async def get_session(self):
        """Get database session"""
        return get_session()
    
    async def get_oath_papers_insights(self) -> Dict[str, Any]:
        """Get AI insights from oath papers"""
        try:
            from sqlalchemy import select
            from ..models.sql_models import OathPaper
            
            session = get_session()
            try:
                # Get all oath papers
                stmt = select(OathPaper)
                result = await session.execute(stmt)
                oath_papers = result.scalars().all()
                
                if not oath_papers:
                    return {
                        "insights": [],
                        "total_papers": 0,
                        "average_learning_value": 0,
                        "recommendations": []
                    }
                
                # Analyze oath papers
                total_papers = len(oath_papers)
                total_learning_value = sum(paper.learning_value or 0 for paper in oath_papers)
                average_learning_value = total_learning_value / total_papers if total_papers > 0 else 0
                
                # Generate insights
                insights = []
                for paper in oath_papers[:5]:  # Top 5 papers
                    insights.append({
                        "id": str(paper.id),
                        "title": paper.title,
                        "learning_value": paper.learning_value or 0,
                        "category": paper.category,
                        "status": paper.status
                    })
                
                # Generate recommendations
                recommendations = []
                if average_learning_value < 0.5:
                    recommendations.append("Average learning value is low - consider improving paper quality")
                
                if total_papers < 10:
                    recommendations.append("Add more oath papers to improve AI learning")
                
                return {
                    "insights": insights,
                    "total_papers": total_papers,
                    "average_learning_value": average_learning_value,
                    "recommendations": recommendations
                }
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error getting oath papers insights", error=str(e))
            return {
                "insights": [],
                "total_papers": 0,
                "average_learning_value": 0,
                "recommendations": []
            }

    async def learn_from_oath_papers(self) -> Dict[str, Any]:
        """Learn from all oath papers"""
        try:
            from sqlalchemy import select
            from ..models.sql_models import OathPaper
            
            session = get_session()
            try:
                # Get all oath papers
                stmt = select(OathPaper).where(OathPaper.status == "completed")
                result = await session.execute(stmt)
                oath_papers = result.scalars().all()
                
                learning_results = {}
                total_learning_value = 0
                
                for paper in oath_papers:
                    # Process each paper
                    analysis = await self.analyze_oath_paper(paper)
                    learning_results[str(paper.id)] = analysis
                    total_learning_value += analysis.get("learning_value", 0)
                
                return {
                    "papers_processed": len(oath_papers),
                    "total_learning_value": total_learning_value,
                    "average_learning_value": total_learning_value / len(oath_papers) if oath_papers else 0,
                    "learning_results": learning_results
                }
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error learning from oath papers", error=str(e))
            return {}

    async def analyze_oath_paper(self, oath_paper) -> Dict[str, Any]:
        """Analyze an oath paper for learning"""
        try:
            # Simple analysis (in a real implementation, use more sophisticated NLP)
            content_length = len(oath_paper.content or "")
            title_length = len(oath_paper.title or "")
            
            # Calculate learning value based on content quality
            learning_value = min(1.0, (content_length + title_length) / 1000)
            
            return {
                "learning_value": learning_value,
                "content_quality": "good" if learning_value > 0.5 else "needs_improvement",
                "needs_improvement": learning_value < 0.5,
                "improvement_suggestions": "Add more detailed content" if learning_value < 0.5 else ""
            }
            
        except Exception as e:
            logger.error("Error analyzing oath paper", error=str(e))
            return {"learning_value": 0, "error": str(e)}

    async def get_learning_progress(self) -> Dict[str, Any]:
        """Get overall learning progress"""
        try:
            from sqlalchemy import select, func
            from ..models.sql_models import OathPaper, Learning
            
            session = get_session()
            try:
                # Get oath papers stats
                stmt = select(func.count(OathPaper.id))
                result = await session.execute(stmt)
                total_papers = result.scalar()
                
                # Get learning entries stats
                stmt = select(func.count(Learning.id))
                result = await session.execute(stmt)
                total_learning_entries = result.scalar()
                
                return {
                    "total_oath_papers": total_papers or 0,
                    "total_learning_entries": total_learning_entries or 0,
                    "system_health": "healthy",
                    "last_updated": datetime.utcnow().isoformat()
                }
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error getting learning progress", error=str(e))
            return {}

    async def get_oath_papers_recommendations(self) -> List[str]:
        """Get recommendations for oath papers"""
        try:
            recommendations = [
                "Add more diverse topics to improve AI learning breadth",
                "Include code examples for better practical learning",
                "Use specific tags for better categorization",
                "Provide detailed descriptions for complex topics"
            ]
            
            return recommendations
            
        except Exception as e:
            logger.error("Error getting recommendations", error=str(e))
            return []

    async def analyze_oath_paper_categories(self) -> Dict[str, Any]:
        """Analyze oath paper categories"""
        try:
            from sqlalchemy import select, func
            from ..models.sql_models import OathPaper
            
            session = get_session()
            try:
                # Get category statistics
                stmt = select(OathPaper.category, func.count(OathPaper.id))
                result = await session.execute(stmt)
                categories = result.all()
                
                category_analysis = {}
                for category, count in categories:
                    category_analysis[category] = {
                        "count": count,
                        "percentage": count / sum(c[1] for c in categories) if categories else 0
                    }
                
                return category_analysis
                
            finally:
                await session.close()
                
        except Exception as e:
            logger.error("Error analyzing categories", error=str(e))
            return {} 

    # Feedback loop for code proposals
    async def propose_code_improvement(self, ai_type: str, proposal_text: str, code_snippet: str = None):
        """Store a code/architecture improvement proposal for review and feedback."""
        # This should insert into a database table (improvement_proposals)
        # For now, just log the proposal
        logger.info("Code improvement proposal", ai_type=ai_type, proposal=proposal_text, code=code_snippet)
        # TODO: Implement DB storage and review workflow 