from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.link import ShortLink
from app.schemas.link import LinkCreate, LinkUpdate, LinkResponse, LinkStats
from app.services.link_service import link_service
from app.services.auth import get_current_active_user, get_current_user
from app.core.config import settings

router = APIRouter(prefix="/links", tags=["Links"])


@router.post("/shorten", response_model=LinkResponse, status_code=status.HTTP_201_CREATED)
async def shorten_url(
    link_data: LinkCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Create a short URL"""
    link = link_service.create_link(db, link_data, current_user)
    
    return LinkResponse(
        short_code=link.short_code,
        original_url=link.original_url,
        short_url=f"{settings.BASE_URL}/{link.short_code}",
        created_at=link.created_at,
        expires_at=link.expires_at
    )


@router.get("/my", response_model=List[LinkResponse])
async def get_my_links(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all links for current user"""
    links = link_service.get_user_links(db, current_user)
    base_url = settings.BASE_URL
    return [
        LinkResponse(
            short_code=link.short_code,
            original_url=link.original_url,
            short_url=f"{base_url}/{link.short_code}",
            created_at=link.created_at,
            expires_at=link.expires_at
        )
        for link in links
    ]

@router.get("/search", response_model=List[LinkResponse])
async def search_links(
    original_url: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Search links by original URL"""
    links = link_service.search_by_original_url(db, original_url)
    
    base_url = settings.BASE_URL
    return [
        LinkResponse(
            short_code=link.short_code,
            original_url=link.original_url,
            short_url=f"{base_url}/{link.short_code}",
            created_at=link.created_at,
            expires_at=link.expires_at
        )
        for link in links
    ]

@router.get("/{short_code}")
async def redirect_to_original_url(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Redirect to original URL"""
    link = link_service.get_link_by_code(db, short_code)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    if link.is_expired():
        link_service.delete_link(db, link)
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Link has expired"
        )
    
    if not link.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link is inactive"
        )
    
    # Increment click count
    link_service.increment_click_count(db, link)
    
    # Redirect
    return RedirectResponse(url=link.original_url, status_code=301)


@router.get("/{short_code}/stats", response_model=LinkStats)
async def get_link_stats(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get link statistics"""
    link = link_service.get_link_by_code(db, short_code)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    # Check ownership if user is authenticated
    if current_user and link.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return LinkStats(
        original_url=link.original_url,
        short_code=link.short_code,
        created_at=link.created_at,
        click_count=link.click_count,
        last_accessed_at=link.last_accessed_at,
        expires_at=link.expires_at
    )


@router.put("/{short_code}", response_model=LinkResponse)
async def update_link(
    short_code: str,
    link_data: LinkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a link (only owner)"""
    link = link_service.get_link_by_code(db, short_code)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    if link.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_link = link_service.update_link(db, link, link_data)
    
    return LinkResponse(
        short_code=updated_link.short_code,
        original_url=updated_link.original_url,
        short_url=f"{settings.BASE_URL}/{updated_link.short_code}",
        created_at=updated_link.created_at,
        expires_at=updated_link.expires_at
    )


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_link(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a link (only owner)"""
    link = link_service.get_link_by_code(db, short_code)
    
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Link not found"
        )
    
    if link.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    link_service.delete_link(db, link)