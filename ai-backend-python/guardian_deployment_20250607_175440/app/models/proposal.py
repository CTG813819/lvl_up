"""
Proposal model using Pydantic
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid
from uuid import UUID


class ProposalBase(BaseModel):
    """Base proposal model"""
    ai_type: str = Field(..., description="AI type: 'Imperium', 'Guardian', 'Sandbox'")
    file_path: str = Field(..., description="Path to the file being modified")
    code_before: str = Field(..., description="Original code")
    code_after: str = Field(..., description="Modified code")
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
    improvement_type: Optional[str] = Field(
        default=None,
        description="Type of improvement",
        pattern="^(performance|readability|security|bug-fix|refactor|feature|system)$"
    )
    confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="AI confidence in this proposal"
    )
    
    # Feedback and learning
    user_feedback_reason: Optional[str] = Field(default=None, description="Why user approved/rejected")
    ai_learning_applied: bool = Field(default=False, description="Whether learning was applied")
    previous_mistakes_avoided: List[str] = Field(default_factory=list, description="List of previous mistakes this proposal avoids")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}


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


class Proposal(ProposalBase):
    """Complete proposal model with ID and timestamps"""
    id: UUID = Field(default_factory=uuid.uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {UUID: str}
        schema_extra = {
            "example": {
                "ai_type": "Imperium",
                "file_path": "lib/main.dart",
                "code_before": "print('Hello World');",
                "code_after": "print('Hello, World!');",
                "status": "pending",
                "improvement_type": "readability",
                "confidence": 0.8
            }
        }


class ProposalResponse(BaseModel):
    """Response model for proposals"""
    id: UUID
    ai_type: str
    file_path: str
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

    class Config:
        from_attributes = True
        json_encoders = {UUID: str}


class ProposalStats(BaseModel):
    """Statistics for proposals"""
    total: int
    pending: int
    approved: int
    rejected: int
    applied: int
    test_passed: int
    test_failed: int 