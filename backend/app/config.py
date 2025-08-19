from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    gemini_api_key: str
    gemini_model: str = "gemini-1.5-flash"
    
    # Database
    database_url: str = "sqlite:///./user_stories.db"
    
    # App Configuration
    app_name: str = "User Story Generator"
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()