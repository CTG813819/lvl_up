"""
Proposal model using Pydantic
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
import uuid
from uuid import UUID


class ProposalBase(BaseModel):
    """Base proposal model"""
    ai_type: str = Field(..., description="AI type: 'Imperium', 'Guardian', 'Sandbox'")
    file_path: str = Field(..., description="Path to the file being modified")
    code_before: str = Field(..., description="Original code")
    code_after: str = Field(..., description="Modified code")
    description: Optional[str] = Field(default=None, description="Proposal description")
    status: str = Field(
        default="pending",
        description="Proposal status",
        pattern="^(pending|approved|rejected|applied|test-passed|test-failed)$"
    )
    result: Optional[str] = Field(default=None, description="Result of the proposal")
    user_feedback: Optional[str] = Field(
        default=None,
        description="User feedback",
        pattern="^(approved|rejected)$"
    )
    test_status: str = Field(
        default="not-run",
        description="Test status",
        pattern="^(not-run|passed|failed)$"
    )
    test_output: Optional[str] = Field(default=None, description="Test output")
    
    # Advanced deduplication fields
    code_hash: Optional[str] = Field(default=None, description="Hash of codeBefore + codeAfter")
    semantic_hash: Optional[str] = Field(default=None, description="Semantic similarity hash")
    diff_score: Optional[float] = Field(default=None, description="Similarity score with existing proposals")
    duplicate_of: Optional[UUID] = Field(default=None, description="Reference to original if duplicate")
    
    # AI Learning fields
    ai_reasoning: Optional[str] = Field(default=None, description="Why the AI made this suggestion")
    learning_context: Optional[str] = Field(default=None, description="Context from previous feedback")
    mistake_pattern: Optional[str] = Field(default=None, description="Pattern of mistakes to avoid")
    improvement_type: Optional[str] = Field(default="general", description="Type of improvement")
    confidence: Optional[float] = Field(default=0.5, description="AI confidence in this proposal")
    user_feedback_reason: Optional[str] = Field(default=None, description="Reason for user feedback")
    ai_learning_applied: Optional[bool] = Field(default=False, description="Whether AI learning was applied")
    previous_mistakes_avoided: Optional[List[str]] = Field(default=[], description="Previous mistakes avoided")
    
    # Enhanced Learning and Change Description Fields
    ai_learning_summary: Optional[str] = Field(default=None, description="What the AI has learned from previous interactions")
    change_type: Optional[str] = Field(default=None, description="Type of change: 'frontend', 'backend', 'database', 'config', 'other'")
    change_scope: Optional[str] = Field(default=None, description="Scope of change: 'minor', 'moderate', 'major', 'critical'")
    affected_components: Optional[List[str]] = Field(default=[], description="List of components affected by this change")
    learning_sources: Optional[List[str]] = Field(default=[], description="Sources of learning (previous proposals, user feedback, etc.)")
    expected_impact: Optional[str] = Field(default=None, description="Expected impact of this change")
    risk_assessment: Optional[str] = Field(default=None, description="Risk assessment of this change")
    
    # Response fields for when proposals are applied
    application_response: Optional[str] = Field(default=None, description="Response message when proposal is applied")
    application_timestamp: Optional[datetime] = Field(default=None, description="When the proposal was applied")
    application_result: Optional[str] = Field(default=None, description="Result of applying the proposal")
    post_application_analysis: Optional[str] = Field(default=None, description="Analysis after applying the proposal")
    
    # Files analyzed during proposal creation
    files_analyzed: Optional[List[str]] = Field(default=[], description="List of files analyzed by the AI when creating this proposal")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={UUID: str}
    )


class ProposalCreate(ProposalBase):
    """Model for creating a new proposal"""
    pass


class ProposalUpdate(BaseModel):
    """Model for updating a proposal"""
    status: Optional[str] = Field(
        default=None,
        pattern="^(pending|approved|rejected|applied|test-passed|test-failed)$"
    )
    result: Optional[str] = None
    user_feedback: Optional[str] = Field(
        default=None,
        pattern="^(approved|rejected)$"
    )
    test_status: Optional[str] = Field(
        default=None,
        pattern="^(not-run|passed|failed)$"
    )
    test_output: Optional[str] = None
    user_feedback_reason: Optional[str] = None
    ai_learning_applied: Optional[bool] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    application_response: Optional[str] = None
    application_result: Optional[str] = None
    post_application_analysis: Optional[str] = None


class Proposal(ProposalBase):
    """Complete proposal model with ID and timestamps"""
    id: UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={UUID: str},
        json_schema_extra={
            "example": {
                "ai_type": "Imperium",
                "file_path": "lib/main.dart",
                "code_before": "print('Hello World');",
                "code_after": "print('Hello, World!');",
                "status": "pending",
                "improvement_type": "readability",
                "confidence": 0.8,
                "change_type": "frontend",
                "change_scope": "minor",
                "ai_learning_summary": "Learned from previous user feedback that code readability is important"
            }
        }
    )


class ProposalResponse(BaseModel):
    """Response model for proposals"""
    id: UUID
    ai_type: str
    file_path: str
    description: Optional[str] = None
    status: str
    improvement_type: Optional[str]
    confidence: float
    created_at: datetime
    user_feedback: Optional[str]
    test_status: str
    updated_at: Optional[datetime] = None
    result: Optional[str] = None
    test_output: Optional[str] = None
    ai_reasoning: Optional[str] = None
    user_feedback_reason: Optional[str] = None
    files_analyzed: Optional[List[str]] = None
    
    # Enhanced fields
    ai_learning_summary: Optional[str] = None
    change_type: Optional[str] = None
    change_scope: Optional[str] = None
    affected_components: Optional[List[str]] = None
    learning_sources: Optional[List[str]] = None
    expected_impact: Optional[str] = None
    risk_assessment: Optional[str] = None
    application_response: Optional[str] = None
    application_result: Optional[str] = None
    post_application_analysis: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {UUID: str}


class ProposalStats(BaseModel):
    """Statistics for proposals"""
    total_proposals: int
    pending_proposals: int
    approved_proposals: int
    rejected_proposals: int
    applied_proposals: int
    test_passed_proposals: int
    test_failed_proposals: int
    average_confidence: float
    improvement_type_distribution: dict
    ai_type_distribution: dict
    change_type_distribution: dict
    recent_activity: List[dict]

    class Config:
        from_attributes = True 