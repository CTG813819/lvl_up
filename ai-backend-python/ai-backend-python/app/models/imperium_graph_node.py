from sqlalchemy import Column, Integer, String, Float, DateTime
from app.core.database import Base
from datetime import datetime

class ImperiumGraphNode(Base):
    __tablename__ = 'imperium_graph_nodes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False)
    agent_type = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    learning_score = Column(Float, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False) 