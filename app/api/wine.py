from fastapi import APIRouter, Depends, HTTPException, status, Query, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime

from app.models.database import get_db
from app.services.storage_service import StorageService
from app.schemas.wine import WineCreate, WineUpdate, WineResponse
from app.models.wine import Wine
from app.config import settings
from app.services import openai_service

router = APIRouter(prefix="/wine", tags=["wine"])

@router.get("/", response_model=List[WineResponse])
async def get_wines(
    storage_id: Optional[str] = Query(None, description="Filter by storage ID"),
    db: Session = Depends(get_db)
):
    """Get all wines, optionally filtered by storage ID"""
    query = db.query(Wine)
    
    if storage_id:
        query = query.filter(Wine.storage_id == storage_id)
    
    return query.all()

@router.get("/{wine_id}", response_model=WineResponse)
async def get_wine(wine_id: str, db: Session = Depends(get_db)):
    """Get a wine by ID"""
    wine = db.query(Wine).filter(Wine.id == wine_id).first()
    
    if not wine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wine not found"
        )
    
    return wine

@router.post("/", response_model=WineResponse, status_code=status.HTTP_201_CREATED)
async def create_wine(
    wine_data: WineCreate,
    db: Session = Depends(get_db)
):
    """Add a new wine"""
    # Validate storage exists
    storage_service = StorageService(db)
    storage = storage_service.get_storage_by_id(wine_data.storage_id)
    
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storage not found"
        )
    
    # Validate position if provided
    if wine_data.position and not storage_service.validate_position(wine_data.storage_id, wine_data.position):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid position or position already occupied"
        )
    
    # Create wine
    db_wine = Wine(
        name=wine_data.name,
        storage_id=wine_data.storage_id,
        position=wine_data.position,
        description=wine_data.description,
        wine_metadata=wine_data.wine_metadata,
        added_date=datetime.utcnow()
    )
    
    db.add(db_wine)
    db.commit()
    db.refresh(db_wine)
    
    return db_wine

@router.post("/analyze-label", status_code=status.HTTP_200_OK)
async def analyze_label(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Analyze a wine label image using OpenAI and return the analysis"""
    try:
        # Save the uploaded file temporarily
        file_location = f"temp_{file.filename}"
        with open(file_location, "wb+") as file_object:
            file_object.write(await file.read())
        
        # Analyze the label using OpenAI
        analysis_result = openai_service.analyze_wine_label(file_location)
        
        # Clean up the temporary file
        os.remove(file_location)
        
        return analysis_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing label: {str(e)}"
        )

@router.put("/{wine_id}", response_model=WineResponse)
async def update_wine(wine_id: str, wine_data: WineUpdate, db: Session = Depends(get_db)):
    """Update a wine"""
    wine = db.query(Wine).filter(Wine.id == wine_id).first()
    
    if not wine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wine not found"
        )
    
    # Handle storage and position validation
    storage_service = StorageService(db)
    
    if wine_data.storage_id and wine_data.storage_id != wine.storage_id:
        # Validate new storage exists
        if not storage_service.get_storage_by_id(wine_data.storage_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage not found"
            )
    
    # Use the existing or new storage_id for position validation
    storage_id = wine_data.storage_id or wine.storage_id
    
    # Validate new position if provided
    if wine_data.position and wine_data.position != wine.position:
        if not storage_service.validate_position(storage_id, wine_data.position):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid position or position already occupied"
            )
    
    # Update fields
    update_data = wine_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(wine, key, value)
    
    db.commit()
    db.refresh(wine)
    
    return wine

@router.delete("/{wine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wine(wine_id: str, db: Session = Depends(get_db)):
    """Delete a wine"""
    wine = db.query(Wine).filter(Wine.id == wine_id).first()
    
    if not wine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wine not found"
        )
    
    db.delete(wine)
    db.commit()
    
    return None