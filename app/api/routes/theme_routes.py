from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_async_db 
import logging
from pydantic import BaseModel
import random
from app.game_state.services.theme_service import ThemeService
from app.api.schemas.theme_schema import ThemeRead
from uuid import UUID
from typing import Optional, List

class ThemeCreatedResponse(BaseModel):
    """Response model for Theme creation"""
    theme_id: str
    message: str

class ThemeOutputResponse(BaseModel):
    """Response model for Theme output"""
    themes: List[ThemeRead]  # Changed field name and used ThemeRead schema
    message: str

router = APIRouter()

@router.post("/", response_model=ThemeCreatedResponse)
async def create_theme(
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
            
        # Generate random Theme name if not provided
        if theme_name is None:
            theme_name = f"test_Theme_{random.randint(1, 1000)}"

        theme_service = ThemeService(db=db)

        # ThemeService.create_Theme must be async and take AsyncSession
        theme = await theme_service.create_theme(
            name=theme_name,
            description=theme_description,
        )
        
        # Return the response
        return ThemeCreatedResponse(
            theme_id=str(theme.entity_id), 
            message="Theme created successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error creating Theme: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/", response_model=ThemeOutputResponse)
async def list_themes(
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
        theme_entities = await theme_service.get_all_themes(skip=skip, limit=limit)
        
        # Convert domain entities to read schemas
        theme_schemas = []
        for entity in theme_entities:
            try:
                schema = await theme_service._convert_entity_to_read_schema(entity)
                if schema:
                    theme_schemas.append(schema)
            except Exception as conv_error:
                logging.warning(f"Error converting theme entity: {conv_error}")
                
        return ThemeOutputResponse(
            themes=theme_schemas, 
            message="Themes retrieved successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error retrieving Themes: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

@router.get("/{theme_id}", response_model=ThemeOutputResponse)
async def get_theme(
        theme_id: UUID,
        db: AsyncSession = Depends(get_async_db)
    ):
    """
    Get a Theme by its ID.
    
    If the Theme is not found, a 404 error will be raised.
    """
    try:
        theme_service = ThemeService(db=db)
        # get_by_id already returns a ThemeRead object
        theme_read_schema = await theme_service.get_by_id(theme_id=theme_id)
        
        if not theme_read_schema:
            raise HTTPException(status_code=404, detail="Theme not found.")
        
        return ThemeOutputResponse(
            themes=[theme_read_schema],  # Return as a list with one item
            message="Theme retrieved successfully"
        )
    except Exception as e:
        # Log the exception for debugging
        logging.exception(f"Error retrieving Theme: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
    
