from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class TrainingData(Base):
    __tablename__ = "training_data"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    subject = Column(String(200), nullable=True, index=True)  # New subject field for AI learning
    description = Column(Text, nullable=False)
    code = Column(Text, nullable=True)  # Optional code field
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, processed, failed
    processed_at = Column(DateTime(timezone=True), nullable=True)
    processing_notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<TrainingData(id={self.id}, title='{self.title}', status='{self.status}')>" 