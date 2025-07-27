
# Fix for async generator issues in AI learning service
import asyncio
from typing import List, Dict, Any
from app.core.database import get_session
from app.models.proposal import Proposal
from sqlalchemy import select

class AILearningService:
    async def get_approved_proposals(self) -> List[Dict[str, Any]]:
        """Get approved proposals for learning"""
        try:
            async with get_session() as db:
                query = select(Proposal).where(Proposal.status == "approved")
                result = await db.execute(query)
                proposals = result.scalars().all()
                return [
                    {
                        "id": str(p.id),
                        "ai_type": p.ai_type,
                        "file_path": p.file_path,
                        "status": p.status,
                        "improvement_type": p.improvement_type
                    }
                    for p in proposals
                ]
        except Exception as e:
            print(f"Error getting approved proposals: {e}")
            return []
    
    async def learn_from_analysis(self, analysis_data: Dict[str, Any]) -> bool:
        """Learn from analysis results"""
        try:
            # Process analysis data
            learning_points = analysis_data.get("learning_points", [])
            
            # Store learning data
            # This would typically save to a learning database
            print(f"Learning from analysis: {len(learning_points)} points")
            return True
        except Exception as e:
            print(f"Error learning from analysis: {e}")
            return False
    
    async def create_quality_proposal(self) -> Dict[str, Any]:
        """Create a high-quality proposal based on learning"""
        try:
            # Get learning data
            learning_data = await self.get_learning_data()
            
            # Create proposal based on learning
            proposal_data = {
                "ai_type": "imperium",
                "file_path": "lib/main.dart",
                "code_before": "// Original code",
                "code_after": "// Improved code based on learning",
                "improvement_type": "learning_based",
                "confidence": 0.8
            }
            
            # Save to database
            async with get_session() as db:
            proposal = Proposal(**proposal_data)
                db.add(proposal)
                await db.commit()
                await db.refresh(proposal)
                
            return {
                "id": str(proposal.id),
                "ai_type": proposal.ai_type,
                "file_path": proposal.file_path,
                "status": proposal.status
            }
    except Exception as e:
            print(f"Error creating quality proposal: {e}")
            return {}
    
    async def get_learning_data(self) -> Dict[str, Any]:
        """Get current learning data"""
        return {
            "total_cycles": 0,
            "success_rate": 0.0,
            "learning_points": []
        }
