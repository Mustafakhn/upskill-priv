from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
from app.db.mysql import get_db_session
from app.api.v1.dao.resource_dao import ResourceDAO
from app.api.v1.services.scrape_service import ScrapeService
from app.api.v1.routers.journey_router import get_user_id

router = APIRouter(prefix="/resource", tags=["resource"])
scrape_service = ScrapeService()


@router.get("/{resource_id}")
def get_resource(
    resource_id: str,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Get a resource by ID"""
    resource = ResourceDAO.get_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.get("/{resource_id}/content")
def get_resource_content(
    resource_id: str,
    user_id: int = Depends(get_user_id),
    db: Session = Depends(get_db_session)
):
    """Get full content of a resource, scraping if needed. Returns both text content and HTML."""
    resource = ResourceDAO.get_by_id(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Check if we have HTML stored in raw_scrapes
    html_content = None
    raw_scrape = ResourceDAO.get_raw_scrape(resource.get("url", ""))
    if raw_scrape:
        html_content = raw_scrape
    
    # If content already exists, return it
    if resource.get("content") and len(resource.get("content", "")) > 100:
        return {
            "content": resource.get("content"),
            "html": html_content,
            "url": resource.get("url"),
            "title": resource.get("title"),
            "scraped": True
        }
    
    # If it's a video, don't scrape
    if resource.get("type") == "video":
        return {
            "content": None,
            "html": None,
            "url": resource.get("url"),
            "title": resource.get("title"),
            "scraped": False,
            "message": "Videos cannot be scraped. Please visit the URL to watch."
        }
    
    # Try to scrape content if missing
    url = resource.get("url")
    if url:
        try:
            scraped_data = scrape_service._scrape_url(url, use_playwright=False)
            if scraped_data:
                # Update resource with scraped content
                if scraped_data.get("content"):
                    ResourceDAO.update(resource_id, {
                        "content": scraped_data.get("content", "")
                    })
                # Save HTML if available
                if scraped_data.get("html"):
                    ResourceDAO.save_raw_scrape(url, scraped_data.get("html"))
                    html_content = scraped_data.get("html")
                
                return {
                    "content": scraped_data.get("content", ""),
                    "html": html_content,
                    "url": url,
                    "title": scraped_data.get("title", resource.get("title")),
                    "scraped": True
                }
        except Exception as e:
            print(f"Error scraping content for {url}: {e}")
    
    # If scraping failed, return what we have
    return {
        "content": resource.get("content", ""),
        "html": html_content,
        "url": url,
        "title": resource.get("title"),
        "scraped": False,
        "message": "Content could not be scraped. Please visit the URL to read the full article."
    }
