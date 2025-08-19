# app/api/stories.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user_story import UserStory
from app.models.epic import Epic
from app.schemas.project import UserStoryCreate, UserStoryResponse
from app.services.gemini import gemini_service

router = APIRouter()

@router.get("/{story_id}", response_model=UserStoryResponse)
def get_user_story(story_id: int, db: Session = Depends(get_db)):
    """Get a specific user story"""
    story = db.query(UserStory).filter(UserStory.id == story_id).first()
    if not story:
        raise HTTPException(status_code=404, detail="User story not found")
    return story

@router.put("/{story_id}", response_model=UserStoryResponse)
def update_user_story(story_id: int, story_update: UserStoryCreate, db: Session = Depends(get_db)):
    """Update a user story"""
    story = db.query(UserStory).filter(UserStory.id == story_id).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="User story not found")
    
    # Update fields
    story.title = story_update.title
    story.user_story = story_update.user_story
    story.acceptance_criteria = story_update.acceptance_criteria
    story.priority = story_update.priority
    story.story_points = story_update.story_points
    
    db.commit()
    db.refresh(story)
    
    return story

@router.delete("/{story_id}")
def delete_user_story(story_id: int, db: Session = Depends(get_db)):
    """Delete a user story"""
    story = db.query(UserStory).filter(UserStory.id == story_id).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="User story not found")
    
    db.delete(story)
    db.commit()
    
    return {"message": "User story deleted successfully"}

@router.post("/{story_id}/refine", response_model=UserStoryResponse)
async def refine_user_story(story_id: int, feedback: str, db: Session = Depends(get_db)):
    """Refine a user story based on feedback (creates a new version)"""
    original_story = db.query(UserStory).filter(UserStory.id == story_id).first()
    
    if not original_story:
        raise HTTPException(status_code=404, detail="User story not found")
    
    try:
        # Get epic context for better refinement
        epic = db.query(Epic).filter(Epic.id == original_story.epic_id).first()
        project = epic.project
        
        # Use Gemini to refine the story
        refined_data = await gemini_service.refine_user_story(
            original_story=original_story.user_story,
            acceptance_criteria=original_story.acceptance_criteria,
            feedback=feedback,
            epic_context=f"{epic.title}: {epic.description}",
            project_context=f"{project.name}: {project.description}"
        )
        
        # Create new version of the story
        new_version = original_story.version + 1
        refined_story = UserStory(
            epic_id=original_story.epic_id,
            title=refined_data["title"],
            user_story=refined_data["user_story"],
            acceptance_criteria=refined_data["acceptance_criteria"],
            priority=refined_data.get("priority", original_story.priority),
            story_points=refined_data.get("story_points", original_story.story_points),
            version=new_version,
            parent_story_id=story_id
        )
        
        db.add(refined_story)
        db.commit()
        db.refresh(refined_story)
        
        return refined_story
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to refine story: {str(e)}")

@router.get("/{story_id}/versions", response_model=List[UserStoryResponse])
def get_story_versions(story_id: int, db: Session = Depends(get_db)):
    """Get all versions of a user story"""
    # Find the root story (version 1 with no parent)
    root_story = db.query(UserStory).filter(UserStory.id == story_id).first()
    if not root_story:
        raise HTTPException(status_code=404, detail="User story not found")
    
    # If this story has a parent, find the root
    while root_story.parent_story_id:
        root_story = db.query(UserStory).filter(UserStory.id == root_story.parent_story_id).first()
    
    # Get all versions starting from root
    versions = db.query(UserStory).filter(
        (UserStory.id == root_story.id) | (UserStory.parent_story_id == root_story.id)
    ).order_by(UserStory.version).all()
    
    return versions