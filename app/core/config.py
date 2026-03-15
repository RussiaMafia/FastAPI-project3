from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )
    
    # Database
    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/url_shortener"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Link settings
    DEFAULT_LINK_EXPIRATION_DAYS: int = 30
    SHORT_CODE_LENGTH: int = 6
    
    # Cache settings
    CACHE_TTL: int = 3600  # 1 hour
    
    # Base URL for generated links
    BASE_URL: str = "http://localhost:8000"

@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()