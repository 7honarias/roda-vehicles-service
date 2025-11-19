import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    ALGORITHM: str
    GCP_PROJECT_ID: str = ""
    GCP_BUCKET_NAME: str = ""
    
    CLOUD_PROVIDER: str = "gcp"
    
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int 
    GOOGLE_APPLICATION_CREDENTIALS: str

    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://roda.com"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()