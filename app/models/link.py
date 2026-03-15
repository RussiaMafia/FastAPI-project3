from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin
from datetime import datetime, timedelta, timezone
from app.core.config import settings


class ShortLink(Base, TimestampMixin):
    __tablename__ = "short_links"
    
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(settings.SHORT_CODE_LENGTH), unique=True, index=True, nullable=False)
    original_url = Column(String, nullable=False)
    custom_alias = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Statistics
    click_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, nullable=True)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="links")
    
    def is_expired(self) -> bool:
        """Check if link is expired"""
        if self.expires_at is None:
            return False
        now = datetime.now(timezone.utc)
        expires = self.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        
        return now > expires
    
    @classmethod
    def generate_expires_at(cls, days: int = None) -> datetime:
        """Generate expiration date"""
        if days is None:
            days = settings.DEFAULT_LINK_EXPIRATION_DAYS
        return datetime.now(timezone.utc) + timedelta(days=days)