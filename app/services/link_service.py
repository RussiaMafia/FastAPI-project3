import string
import random
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.link import ShortLink
from app.models.user import User
from app.schemas.link import LinkCreate, LinkUpdate
from app.core.redis_client import cache
from datetime import datetime, timezone


class LinkService:
    @staticmethod
    def generate_short_code(length: int = 6) -> str:
        """Generate random short code"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def create_link(db: Session, link_data: LinkCreate, owner: Optional[User] = None) -> ShortLink:
        """Create a new short link"""
        # Check if custom alias is provided and unique
        if link_data.custom_alias:
            existing = db.query(ShortLink).filter(
                ShortLink.short_code == link_data.custom_alias
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Custom alias already exists"
                )
            short_code = link_data.custom_alias
        else:
            # Generate unique short code
            while True:
                short_code = LinkService.generate_short_code()
                if not db.query(ShortLink).filter(ShortLink.short_code == short_code).first():
                    break

        expires_at = link_data.expires_at
        if expires_at is not None:
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        # Create link
        db_link = ShortLink(
            short_code=short_code,
            original_url=str(link_data.original_url),
            custom_alias=link_data.custom_alias,
            expires_at=expires_at,
            owner_id=owner.id if owner else None
        )
        
        db.add(db_link)
        db.commit()
        db.refresh(db_link)
        
        return db_link
    
    @staticmethod
    def get_link_by_code(db: Session, short_code: str) -> Optional[ShortLink]:
        """Get link by short code"""
        # Try cache first
        cache_key = f"link:{short_code}"
        cached_link = cache.get(cache_key)
        if cached_link:
            return ShortLink(**cached_link)
        
        # Get from database
        link = db.query(ShortLink).filter(ShortLink.short_code == short_code).first()
        
        # Cache the link
        if link:
            cache.set(cache_key, link.__dict__)
        
        return link
    
    @staticmethod
    def increment_click_count(db: Session, link: ShortLink) -> None:
        """Increment click count and update last accessed time"""
        link.click_count += 1
        link.last_accessed_at = datetime.utcnow()
        db.commit()
        
        # Invalidate cache
        cache.delete(f"link:{link.short_code}")
    
    @staticmethod
    def update_link(db: Session, link: ShortLink, update_data: LinkUpdate) -> ShortLink:
        """Update link"""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        if "original_url" in update_dict:
            update_dict["original_url"] = str(update_dict["original_url"])
        
        if "expires_at" in update_dict and update_dict["expires_at"] is not None:
            if update_dict["expires_at"].tzinfo is None:
                update_dict["expires_at"] = update_dict["expires_at"].replace(tzinfo=timezone.utc)

        for key, value in update_dict.items():
            setattr(link, key, value)
        
        db.commit()
        db.refresh(link)
        
        # Invalidate cache
        cache.delete(f"link:{link.short_code}")
        
        return link
    
    @staticmethod
    def delete_link(db: Session, link: ShortLink) -> bool:
        """Delete link"""
        db.delete(link)
        db.commit()
        
        # Invalidate cache
        cache.delete(f"link:{link.short_code}")
        
        return True
    
    @staticmethod
    def search_by_original_url(db: Session, original_url: str) -> List[ShortLink]:
        """Search links by original URL"""
        return db.query(ShortLink).filter(
            ShortLink.original_url.like(f"%{original_url}%")
        ).all()
    
    @staticmethod
    def get_user_links(db: Session, user: User) -> List[ShortLink]:
        """Get all links for a user"""
        return db.query(ShortLink).filter(ShortLink.owner_id == user.id).all()
    
    @staticmethod
    def cleanup_expired_links(db: Session) -> int:
        """Delete expired links"""
        expired_links = db.query(ShortLink).filter(
            ShortLink.expires_at < datetime.utcnow()
        ).all()
        
        count = len(expired_links)
        for link in expired_links:
            db.delete(link)
            cache.delete(f"link:{link.short_code}")
        
        db.commit()
        return count


link_service = LinkService()