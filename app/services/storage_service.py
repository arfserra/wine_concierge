from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.storage import Storage
from app.models.wine import Wine
from app.schemas.storage import StorageCreate, StorageUpdate

class StorageService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all_storages(self) -> List[Storage]:
        """Get all storage configurations"""
        return self.db.query(Storage).all()
    
    def get_storage_by_id(self, storage_id: str) -> Optional[Storage]:
        """Get a storage configuration by ID"""
        return self.db.query(Storage).filter(Storage.id == storage_id).first()
    
    def create_storage(self, storage_data: StorageCreate) -> Storage:
        """Create a new storage configuration"""
        # Calculate total positions
        total_positions = 0
        for zone in storage_data.zones:
            zone_positions = 1
            for dimension_value in zone.dimensions.values():
                zone_positions *= dimension_value
            total_positions += zone_positions
        
        # Create storage object
        db_storage = Storage(
            name=storage_data.name,
            type=storage_data.type,
            zones=[zone.model_dump() for zone in storage_data.zones],
            total_positions=total_positions,
            position_naming_scheme=storage_data.position_naming_scheme
        )
        
        self.db.add(db_storage)
        self.db.commit()
        self.db.refresh(db_storage)
        
        return db_storage
    
    def update_storage(self, storage_id: str, storage_data: StorageUpdate) -> Storage:
        """Update a storage configuration"""
        db_storage = self.get_storage_by_id(storage_id)
        
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
    
    def delete_storage(self, storage_id: str) -> bool:
        """Delete a storage configuration"""
        db_storage = self.get_storage_by_id(storage_id)
        
        if not db_storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage configuration not found"
            )
        
        self.db.delete(db_storage)
        self.db.commit()
        
        return True
    
    def validate_position(self, storage_id: str, position: str) -> bool:
        """
        Validate if a position is valid for a given storage
        
        Args:
            storage_id: The ID of the storage
            position: The position string (e.g., "A3", "Red Zone-B2")
            
        Returns:
            bool: True if the position is valid, False otherwise
        """
        storage = self.get_storage_by_id(storage_id)
        if not storage:
            return False
        
        # Empty position is considered valid (wine has no specific position)
        if not position:
            return True
        
        # For simplicity, we'll just check if the position is already occupied
        existing_wine = self.db.query(Wine).filter(
            Wine.storage_id == storage_id,
            Wine.position == position
        ).first()
        
        if existing_wine:
            return False
        
        return