from pydantic_settings import BaseSettings, SettingsConfigDict
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
    LOG_LEVEL: str = "INFO"
    MOCK_EMAIL: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings(): 
    return Settings()
settings = get_settings()