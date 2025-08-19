from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Project Schemas
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    app_type: str
    context: str

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    app_type: Optional[str] = None
    context: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Epic Schemas
class EpicBase(BaseModel):
    title: str
    description: Optional[str] = None

class EpicCreate(EpicBase):
    project_id: int

class EpicResponse(EpicBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# User Story Schemas
class UserStoryBase(BaseModel):
    title: str
    user_story: str
    acceptance_criteria: List[str]
    priority: str = "Medium"
    story_points: Optional[int] = None

class UserStoryCreate(UserStoryBase):
    pass

class UserStoryResponse(UserStoryBase):
    id: int
    epic_id: int
    version: int
    parent_story_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Request schemas for operations
class GenerateEpicsRequest(BaseModel):
    """Request body for generating epics (optional, can be empty)"""
    additional_context: Optional[str] = None

class RefineStoryRequest(BaseModel):
    """Request body for refining a user story"""
    feedback: str