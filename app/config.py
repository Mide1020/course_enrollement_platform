from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    
    
    # Database key
    DATABASE_URL: str
    
    # Security key
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application  key
    APP_NAME: str = "Course Enrollment Platform"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings(): 
    return Settings()
settings = get_settings()