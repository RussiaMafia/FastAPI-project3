from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None


class LinkUpdate(BaseModel):
    original_url: Optional[HttpUrl] = None
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None


class LinkStats(BaseModel):
    original_url: str
    short_code: str
    created_at: datetime
    click_count: int
    last_accessed_at: Optional[datetime]
    expires_at: Optional[datetime]


class LinkResponse(BaseModel):
    short_code: str
    original_url: str
    short_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True