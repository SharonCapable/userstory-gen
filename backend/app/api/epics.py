from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.epic import Epic
from app.models.user_story import UserStory
from app.schemas.project import EpicResponse, UserStoryCreate, UserStoryResponse
from app.services.gemini import gemini_service

router = APIRouter()

@router.get("/{epic_id}", response_model=EpicResponse)
def get_epic(epic_id: int, db: Session = Depends(get_db)):
    """Get a specific epic with its details"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    return epic

@router.get("/{epic_id}/stories", response_model=List[UserStoryResponse])
def get_epic_stories(epic_id: int, db: Session = Depends(get_db)):
    """Get all user stories for a specific epic"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    stories = db.query(UserStory).filter(UserStory.epic_id == epic_id).all()
    return stories

@router.post("/{epic_id}/generate-stories", response_model=List[UserStoryResponse])
async def generate_user_stories(epic_id: int, db: Session = Depends(get_db)):
    """Generate user stories for an epic using AI"""
    epic = db.query(Epic).filter(Epic.id == epic_id).first()
    if not epic:
        raise HTTPException(status_code=404, detail="Epic not found")
    
    # Get project context
    project = epic.project
    
    try:
        # Generate stories using Gemini
        stories_data = await gemini_service.generate_user_stories(
            epic_title=epic.title,
            epic_description=epic.description,
            project_context=f"{project.name}: {project.description}",
            app_type=project.app_type
        )
        
        # Create and save stories to database
        created_stories = []
        for story_data in stories_data:
            story = UserStory(
                epic_id=epic_id,
                title=story_data["title"],
                user_story=story_data["user_story"],
                acceptance_criteria=story_data["acceptance_criteria"],
                priority=story_data.get("priority", "Medium"),
                story_points=story_data.get("story_points", 3),
                version=1
            )
            db.add(story)
            created_stories.append(story)
        
        db.commit()
        
        # Refresh to get IDs
        for story in created_stories:
            db.refresh(story)
        
        return created_stories
        
    except Exception as e:
        db.rollback()
        print(f"Error in generate_user_stories: {e}")  # This will show in your FastAPI logs
        raise HTTPException(status_code=500, detail=f"Failed to generate stories: {str(e)}")


@router.put("/{epic_id}/stories/{story_id}", response_model=UserStoryResponse)
def update_user_story(epic_id: int, story_id: int, story_update: UserStoryCreate, db: Session = Depends(get_db)):
    """Update a user story"""
    story = db.query(UserStory).filter(
        UserStory.id == story_id, 
        UserStory.epic_id == epic_id
    ).first()
    
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

@router.delete("/{epic_id}/stories/{story_id}")
def delete_user_story(epic_id: int, story_id: int, db: Session = Depends(get_db)):
    """Delete a user story"""
    story = db.query(UserStory).filter(
        UserStory.id == story_id, 
        UserStory.epic_id == epic_id
    ).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="User story not found")
    
    db.delete(story)
    db.commit()
    
    return {"message": "User story deleted successfully"}