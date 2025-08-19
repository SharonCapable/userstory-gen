# app/api/projects.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Project, Epic
from app.schemas.project import (
    ProjectCreate, 
    ProjectResponse, 
    ProjectUpdate,
    GenerateEpicsRequest,
    EpicResponse
)
from app.services.gemini import gemini_service

router = APIRouter()

@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    """Create a new project"""
    db_project = Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/", response_model=List[ProjectResponse])
def get_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all projects"""
    projects = db.query(Project).offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project: ProjectUpdate, db: Session = Depends(get_db)):
    """Update a project"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update_data = project.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_project, field, value)
    
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project"""
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

@router.post("/{project_id}/generate-epics", response_model=List[EpicResponse])
async def generate_epics(
    project_id: int, 
    db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Create the project_context dictionary that your Gemini service expects
        project_context = {
            'app_type': project.app_type,
            'name': project.name,
            'description': project.description,
            'context': project.context
        }
        
        # Call your existing generate_epics method with the correct parameter
        epics_data = gemini_service.generate_epics(project_context)
        
        # Save epics to database
        created_epics = []
        for epic_data in epics_data:
            epic = Epic(
                project_id=project_id,
                title=epic_data["title"],
                description=epic_data["description"]
            )
            db.add(epic)
            created_epics.append(epic)
        
        db.commit()
        
        # Refresh to get IDs
        for epic in created_epics:
            db.refresh(epic)
        
        return created_epics
        
    except Exception as e:
        db.rollback()
        print(f"Error in generate_epics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate epics: {str(e)}")
    

@router.get("/{project_id}/epics", response_model=List[EpicResponse])
def get_project_epics(project_id: int, db: Session = Depends(get_db)):
    """Get all epics for a project"""
    epics = db.query(Epic).filter(Epic.project_id == project_id).all()
    return epics