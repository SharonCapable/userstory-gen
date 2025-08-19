# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.config import settings
from app.api import projects, epics, stories
from app.services.gemini import gemini_service

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test endpoint
@app.get("/")
def read_root():
    return {"message": "User Story Generator API", "status": "running"}

@app.get("/api/test-gemini")
def test_gemini():
    """Test if Gemini API is properly configured"""
    if gemini_service.test_connection():
        return {"status": "success", "message": "Gemini API connected successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to connect to Gemini API")

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(epics.router, prefix="/api/epics", tags=["epics"])
app.include_router(stories.router, prefix="/api/stories", tags=["stories"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)