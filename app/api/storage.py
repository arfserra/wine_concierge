from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.services.storage_service import StorageService
from app.schemas.storage import StorageCreate, StorageUpdate, StorageResponse

router = APIRouter(prefix="/storage", tags=["storage"])

@router.get("/", response_model=List[StorageResponse])
async def get_storage_configurations(db: Session = Depends(get_db)):
    """Get all storage configurations"""
    storage_service = StorageService(db)
    return storage_service.get_all_storages()

@router.get("/{storage_id}", response_model=StorageResponse)
async def get_storage_configuration(storage_id: str, db: Session = Depends(get_db)):
    """Get a single storage configuration by ID"""
    storage_service = StorageService(db)
    storage = storage_service.get_storage_by_id(storage_id)
    
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storage configuration not found"
        )
    
    return storage

@router.post("/", response_model=StorageResponse, status_code=status.HTTP_201_CREATED)
async def create_storage_configuration(storage_data: StorageCreate, db: Session = Depends(get_db)):
    """Create a new storage configuration"""
    storage_service = StorageService(db)
    return storage_service.create_storage(storage_data)

@router.put("/{storage_id}", response_model=StorageResponse)
async def update_storage_configuration(storage_id: str, storage_data: StorageUpdate, db: Session = Depends(get_db)):
    """Update a storage configuration"""
    storage_service = StorageService(db)
    return storage_service.update_storage(storage_id, storage_data)

@router.delete("/{storage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_storage_configuration(storage_id: str, db: Session = Depends(get_db)):
    """Delete a storage configuration"""
    storage_service = StorageService(db)
    storage_service.delete_storage(storage_id)
    return None