# app/models/user_story.py
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class UserStory(Base):
    __tablename__ = "user_stories"
    
    id = Column(Integer, primary_key=True, index=True)
    epic_id = Column(Integer, ForeignKey("epics.id"))
    title = Column(String(200), nullable=False)
    user_story = Column(Text)  # The actual "As a... I want... So that..." text
    acceptance_criteria = Column(JSON)  # List of acceptance criteria
    priority = Column(String(20))  # high, medium, low
    story_points = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # For versioning
    version = Column(Integer, default=1)
    parent_story_id = Column(Integer, ForeignKey("user_stories.id"), nullable=True)
    
    # Relationships
    epic = relationship("Epic", back_populates="user_stories")
    parent_story = relationship("UserStory", remote_side=[id])