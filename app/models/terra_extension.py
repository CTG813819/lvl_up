from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime

class TerraExtension(Base):
    __tablename__ = "terra_extensions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    feature_name = Column(String, nullable=False)
    menu_title = Column(String, nullable=False)
    icon_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    dart_code = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="submitted")  # submitted, testing, ready_for_approval, approved, rejected, failed
    user_id = Column(String, nullable=True)
    test_results = Column(JSON, nullable=True)
    ai_analysis = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, server_default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "feature_name": self.feature_name,
            "menu_title": self.menu_title,
            "icon_name": self.icon_name,
            "description": self.description,
            "status": self.status,
            "user_id": self.user_id,
            "test_results": self.test_results,
            "ai_analysis": self.ai_analysis,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        } 