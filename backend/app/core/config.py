from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/room_decorator"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # API Keys (will be added later)
    MESHY_API_KEY: Optional[str] = None
    MESHY_TEST_MODE: bool = True
    
    # AWS (will be added later)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    S3_BUCKET_NAME: Optional[str] = None
    
    # App Settings
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-change-this"
    
    class Config:
        env_file = ".env"

settings = Settings()
