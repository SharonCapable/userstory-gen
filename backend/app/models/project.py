# app/models/project.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    app_type = Column(String(100))  # e.g., "geospatial", "finance", "ecommerce"
    context = Column(Text)  # Detailed context about the project
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    epics = relationship("Epic", back_populates="project", cascade="all, delete-orphan")