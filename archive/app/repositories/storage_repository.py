from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.storage import Storage
from app.schemas.storage import StorageCreate, StorageUpdate


class StorageRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, user_id: str) -> List[Storage]:
        """Get all storage configurations for a user"""
        return self.db.query(Storage).filter(Storage.user_id == user_id).all()
    
    def get_by_id(self, storage_id: str, user_id: str) -> Optional[Storage]:
        """Get a storage configuration by ID"""
        storage = self.db.query(Storage).filter(
            Storage.id == storage_id,
            Storage.user_id == user_id
        ).first()
        
        return storage
    
    def create(self, storage_data: StorageCreate, user_id: str) -> Storage:
        """Create a new storage configuration"""
        # Calculate total positions
        total_positions = 0
        for zone in storage_data.zones:
            zone_positions = 1
            for dimension_value in zone.dimensions.values():
                zone_positions *= dimension_value
            total_positions += zone_positions
        
        # Create the storage object
        db_storage = Storage(
            name=storage_data.name,
            type=storage_data.type,
            zones=[zone.model_dump() for zone in storage_data.zones],
            total_positions=total_positions,
            position_naming_scheme=storage_data.position_naming_scheme,
            user_id=user_id
        )
        
        self.db.add(db_storage)
        self.db.commit()
        self.db.refresh(db_storage)
        
        return db_storage
    
    def update(self, storage_id: str, user_id: str, storage_data: StorageUpdate) -> Storage:
        """Update a storage configuration"""
        db_storage = self.get_by_id(storage_id, user_id)
        
        if not db_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage configuration not found"
            )
        
        # Update fields if provided
        update_data = storage_data.model_dump(exclude_unset=True)
        
        # If zones are updated, recalculate total positions
        if "zones" in update_data:
            total_positions = 0
            for zone in update_data["zones"]:
                zone_positions = 1
                for dimension_value in zone["dimensions"].values():
                    zone_positions *= dimension_value
                total_positions += zone_positions
            
            update_data["total_positions"] = total_positions
        
        for key, value in update_data.items():
            setattr(db_storage, key, value)
        
        self.db.commit()
        self.db.refresh(db_storage)
        
        return db_storage
    
    def delete(self, storage_id: str, user_id: str) -> bool:
        """Delete a storage configuration"""
        db_storage = self.get_by_id(storage_id, user_id)
        
        if not db_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage configuration not found"
            )
        
        self.db.delete(db_storage)
        self.db.commit()
        
        return True