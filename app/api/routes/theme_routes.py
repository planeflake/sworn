from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db 
import logging
from pydantic import BaseModel
import random
from app.game_state.models.theme import ThemeEntity
from app.game_state.services.theme_service import ThemeService
import uuid
from typing import Optional

class ThemeCreatedResponse(BaseModel):
    """Response model for Theme creation"""
    theme_id: str
    message: str

class ThemeOutputResponse(BaseModel):
    """Response model for Theme output"""
    theme: ThemeEntity
    message: str

router = APIRouter()

@router.post("/", response_model=ThemeCreatedResponse)
async def create_Theme(
        theme_id: Optional[str] = Body(default=None),
        theme_name: Optional[str] = Body(default=None),
        theme_description: Optional[str] = Body(default=None),
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Create a new Theme with the given ID.
    
    If Theme_id is not provided, a random UUID will be generated.
    If Theme_name is not provided, a random test Theme name will be generated.
    """
    try:
        # Generate UUID at runtime if not provided
        if theme_id is None:
            theme_id = str(uuid.uuid4())
            
        # Generate random Theme name if not provided
        if theme_name is None:
            theme_name = f"test_Theme_{random.randint(1, 1000)}"
            
        # ThemeService.create_Theme must be async and take AsyncSession
        theme = await ThemeService.create_theme(
            db=db,
            theme_id=theme_id,
            name=theme_name,
            description=theme_description,
        )
        
        # Return the response
        return ThemeCreatedResponse(
            theme_id=str(theme.id), 
            message="Theme created successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error creating Theme: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/", response_model=ThemeOutputResponse)
async def list_Themes(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    List all Themes with pagination.
    
    Returns a list of Themes with a message.
    """
    try:
        theme_service = ThemeService(db=db)
        themes = await theme_service.get_all_themes(skip=skip, limit=limit)
        
        return ThemeOutputResponse(
            theme=themes, 
            message="Themes retrieved successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error retrieving Themes: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/{theme_id}", response_model=ThemeOutputResponse)
async def get_Theme(
        theme_id: str,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Get a Theme by its ID.
    
    If the Theme is not found, a 404 error will be raised.
    """
    try:
        theme_service = ThemeService(db=db)
        theme = await theme_service.get_by_id(theme_id=theme_id)
        
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found.")
        
        return ThemeOutputResponse(
            theme=theme, 
            message="Theme retrieved successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error retrieving Theme: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
