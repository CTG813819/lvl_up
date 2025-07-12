"""
Oath Paper Pydantic models
"""

from pydantic import BaseModel
from typing import Dict, Optional, Any
from datetime import datetime


class OathPaperResponse(BaseModel):
    """Response model for Oath Paper"""
    id: str
    title: str
    content: str
    category: str
    ai_insights: Optional[Dict[str, Any]] = None
    learning_value: float = 0.0
    status: str = "pending"
    ai_responses: Dict[str, Any] = {}
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class OathPaperCreate(BaseModel):
    """Create model for Oath Paper"""
    title: str
    content: str
    category: str = "general"


class OathPaperUpdate(BaseModel):
    """Update model for Oath Paper"""
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    ai_insights: Optional[Dict[str, Any]] = None
    learning_value: Optional[float] = None
    status: Optional[str] = None 