from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.models.database import get_db
from app.repositories.wine_repository import WineRepository
from app.schemas.wine import WineCreate, WineUpdate, WineInDB
from app.dependencies import get_current_user_id
from app.services import image_service, openai_service

router = APIRouter(prefix="/wines", tags=["wines"])

@router.get("/", response_model=List[WineInDB])
async def get_wines(
    storage_id: Optional[str] = Query(None, description="Filter by storage ID"),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get all wines in the user's collection."""
    wine_repo = WineRepository(db)
    return wine_repo.get_all(user_id, storage_id=storage_id)

@router.get("/{wine_id}", response_model=WineInDB)
async def get_wine(
    wine_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get a specific wine by ID."""
    wine_repo = WineRepository(db)
    wine = wine_repo.get_by_id(wine_id, user_id)
    
    if not wine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wine not found"
        )
    
    return wine

@router.post("/", response_model=WineInDB, status_code=status.HTTP_201_CREATED)
async def add_wine(
    wine_data: str = Form(...),
    label_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Add a new wine to the collection, optionally with label image for analysis."""
    try:
        # Parse wine data from form
        wine_data_dict = json.loads(wine_data)
        wine_create = WineCreate(**wine_data_dict)
        
        # If an image was uploaded, process it
        if label_image:
            # Save the image
            image_path = await image_service.save_wine_label(label_image)
            wine_create.label_image_url = image_path
            
            # Analyze the image with OpenAI
            full_path = f"{image_service.upload_dir}/{image_path}"
            analysis_result = openai_service.analyze_wine_label(full_path)
            
            if analysis_result["success"]:
                # Use AI extracted data to fill in missing fields
                extracted_data = analysis_result["data"]
                
                # Only update fields that were not provided by the user
                if not wine_create.name and extracted_data.get("name"):
                    wine_create.name = extracted_data["name"]
                    
                if not wine_create.producer and extracted_data.get("producer"):
                    wine_create.producer = extracted_data["producer"]
                    
                if not wine_create.vintage and extracted_data.get("vintage"):
                    wine_create.vintage = extracted_data["vintage"]
                    
                if not wine_create.region and extracted_data.get("region"):
                    wine_create.region = extracted_data["region"]
                    
                if not wine_create.country and extracted_data.get("country"):
                    wine_create.country = extracted_data["country"]
                    
                if not wine_create.varietal and extracted_data.get("varietal"):
                    wine_create.varietal = extracted_data["varietal"]
                    
                if not wine_create.type and extracted_data.get("type"):
                    wine_create.type = extracted_data["type"]
                
                # Add metadata from analysis
                if not wine_create.metadata:
                    wine_create.metadata = {}
                    
                wine_create.metadata["ai_analysis"] = {
                    "confidence_score": analysis_result["confidence_score"],
                    "raw_response": analysis_result["raw_response"]
                }
        
        # Create the wine
        wine_repo = WineRepository(db)
        return wine_repo.create(wine_create, user_id)
        
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON in wine_data"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while adding the wine: {str(e)}"
        )

@router.put("/{wine_id}", response_model=WineInDB)
async def update_wine(
    wine_id: str,
    wine_data: WineUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Update a wine's information."""
    wine_repo = WineRepository(db)
    return wine_repo.update(wine_id, user_id, wine_data)

@router.delete("/{wine_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wine(
    wine_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Remove a wine from the collection."""
    wine_repo = WineRepository(db)
    wine_repo.delete(wine_id, user_id)
    return None