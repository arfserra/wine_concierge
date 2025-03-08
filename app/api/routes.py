from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models.storage import Storage
from app.models.wine import Wine
from app.schemas.storage import StorageCreate, StorageUpdate, StorageInDB
from app.schemas.wine import WineCreate, WineUpdate, WineInDB
from app.services import image_service, openai_service

router = APIRouter()

# Storage routes
@router.get("/storage")
async def get_storage_configurations(db: Session = Depends(get_db)):
    """Get all storage configurations for the current user."""
    storages = db.query(Storage).all()
    return storages

@router.post("/storage", status_code=status.HTTP_201_CREATED)
async def create_storage_configuration(storage: StorageCreate, db: Session = Depends(get_db)):
    """Create a new storage configuration."""
    new_storage = Storage(**storage.dict(), user_id="current_user")  # Replace with actual user ID
    db.add(new_storage)
    db.commit()
    db.refresh(new_storage)
    return new_storage

@router.get("/storage/{storage_id}")
async def get_storage_configuration(storage_id: str, db: Session = Depends(get_db)):
    """Get a specific storage configuration."""
    storage = db.query(Storage).filter(Storage.id == storage_id).first()
    if not storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    return storage

@router.put("/storage/{storage_id}")
async def update_storage_configuration(storage_id: str, storage_update: StorageUpdate, db: Session = Depends(get_db)):
    """Update a storage configuration."""
    storage = db.query(Storage).filter(Storage.id == storage_id).first()
    if not storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    
    update_data = storage_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(storage, key, value)
    
    db.commit()
    db.refresh(storage)
    return storage

@router.delete("/storage/{storage_id}")
async def delete_storage_configuration(storage_id: str, db: Session = Depends(get_db)):
    """Delete a storage configuration."""
    storage = db.query(Storage).filter(Storage.id == storage_id).first()
    if not storage:
        raise HTTPException(status_code=404, detail="Storage not found")
    
    db.delete(storage)
    db.commit()
    return {"detail": "Storage deleted successfully"}

# Wine routes
@router.get("/wines")
async def get_wines(db: Session = Depends(get_db)):
    """Get all wines in collection."""
    wines = db.query(Wine).all()
    return wines

@router.post("/wines", status_code=status.HTTP_201_CREATED)
async def add_wine(
    wine_data: str = Form(...),
    label_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Add a new wine to collection."""
    # Parse the wine data JSON
    import json
    wine_dict = json.loads(wine_data)
    
    # Save the label image if provided
    if label_image:
        wine_dict["label_image_url"] = await image_service.save_wine_label(label_image)
    
    # Create wine record
    wine = WineCreate(**wine_dict)
    new_wine = Wine(**wine.dict(), user_id="current_user")  # Replace with actual user ID
    
    db.add(new_wine)
    db.commit()
    db.refresh(new_wine)
    
    return new_wine

@router.post("/wines/analyze")
async def analyze_wine_label(label_image: UploadFile = File(...)):
    """Analyze a wine label image and extract information."""
    # Save the uploaded image temporarily
    import tempfile
    import os
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    try:
        contents = await label_image.read()
        with open(temp_file.name, "wb") as f:
            f.write(contents)
        
        # Analyze the label using OpenAI service
        analysis_result = openai_service.analyze_wine_label(temp_file.name)
        
        # Save the image permanently if analysis was successful
        if analysis_result["success"]:
            saved_image_path = await image_service.save_wine_label(label_image)
            analysis_result["label_image_url"] = saved_image_path
        
        return analysis_result
    finally:
        temp_file.close()
        os.unlink(temp_file.name)

# Recommendation routes
@router.post("/recommendations/pairing")
async def get_wine_pairing(
    food_description: str = Form(...),
    db: Session = Depends(get_db)
):
    """Get wine pairing recommendations based on food description."""
    # Get available wines from collection
    wines = db.query(Wine).all()
    
    if not wines:
        return {
            "success": False,
            "error": "No wines in collection. Please add wines first."
        }
    
    # Get pairing recommendations
    result = openai_service.get_wine_pairing(food_description, wines)
    return result

@router.post("/recommendations/image")
async def analyze_food_image(
    food_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Analyze food image and recommend wine pairings."""
    # Get available wines from collection
    wines = db.query(Wine).all()
    
    if not wines:
        return {
            "success": False,
            "error": "No wines in collection. Please add wines first."
        }
    
    # Save the uploaded image temporarily
    import tempfile
    import os
    
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    try:
        contents = await food_image.read()
        with open(temp_file.name, "wb") as f:
            f.write(contents)
        
        # Analyze the food image and get pairing
        result = openai_service.analyze_food_image(temp_file.name, wines)
        
        return result
    finally:
        temp_file.close()
        os.unlink(temp_file.name)