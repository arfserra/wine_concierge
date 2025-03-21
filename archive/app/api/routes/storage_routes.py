from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.models.database import get_db
from app.repositories.storage_repository import StorageRepository
from app.schemas.storage import StorageCreate, StorageUpdate, StorageInDB
from app.dependencies import get_current_user_id

router = APIRouter(prefix="/storage", tags=["storage"])

@router.get("/", response_model=List[StorageInDB])
async def get_storage_configurations(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get all storage configurations for the current user."""
    storage_repo = StorageRepository(db)
    return storage_repo.get_all(user_id)

@router.get("/{storage_id}", response_model=StorageInDB)
async def get_storage_configuration(
    storage_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get a single storage configuration by ID."""
    storage_repo = StorageRepository(db)
    storage = storage_repo.get_by_id(storage_id, user_id)
    
    if not storage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Storage configuration not found"
        )
    
    return storage

@router.post("/", response_model=StorageInDB, status_code=status.HTTP_201_CREATED)
async def create_storage_configuration(
    storage_data: StorageCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Create a new storage configuration."""
    storage_repo = StorageRepository(db)
    return storage_repo.create(storage_data, user_id)

@router.put("/{storage_id}", response_model=StorageInDB)
async def update_storage_configuration(
    storage_id: str,
    storage_data: StorageUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Update a storage configuration."""
    storage_repo = StorageRepository(db)
    return storage_repo.update(storage_id, user_id, storage_data)

@router.delete("/{storage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_storage_configuration(
    storage_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Delete a storage configuration."""
    storage_repo = StorageRepository(db)
    storage_repo.delete(storage_id, user_id)
    return None