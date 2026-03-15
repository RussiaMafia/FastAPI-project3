from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.link_service import link_service

# Роутер без префикса — для чистых ссылок
router = APIRouter(tags=["Public Redirect"])


@router.get("/{short_code}", include_in_schema=False)
async def public_redirect(
    short_code: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Публичный редирект по короткой ссылке"""
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
    
    # Считаем клик
    link_service.increment_click_count(db, link)
    
    # Редирект
    return RedirectResponse(url=link.original_url, status_code=301)