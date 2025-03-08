from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.wine import Wine
from app.models.storage import Storage
from app.schemas.wine import WineCreate, WineUpdate
from app.utils.position_validator import PositionValidator

class WineRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_all(self, user_id: str, storage_id: Optional[str] = None) -> List[Wine]:
        """Get all wines for a user, optionally filtered by storage"""
        query = self.db.query(Wine).filter(Wine.user_id == user_id)
        
        if storage_id:
            query = query.filter(Wine.storage_id == storage_id)
            
        return query.all()
    
    def get_by_id(self, wine_id: str, user_id: str) -> Optional[Wine]:
        """Get a wine by ID"""
        return self.db.query(Wine).filter(
            Wine.id == wine_id,
            Wine.user_id == user_id
        ).first()
    
    def create(self, wine_data: WineCreate, user_id: str) -> Wine:
        """Create a new wine entry"""
        # Validate storage exists and belongs to user
        storage = self.db.query(Storage).filter(
            Storage.id == wine_data.storage_id,
            Storage.user_id == user_id
        ).first()
        
        if not storage:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Storage not found"
            )
        
        # Validate position if provided
        if wine_data.position:
            if not PositionValidator.validate_position(wine_data.position, storage):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid position for this storage configuration"
                )
            
            # Check if position is already occupied
            if PositionValidator.is_position_occupied(wine_data.position, storage.id, self.db):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Position already occupied by another wine"
                )
        
        # Create wine object with adjusted fields
        wine_dict = wine_data.model_dump()
        
        # Handle renaming of 'metadata' field to 'wine_metadata' for the database model
        if 'metadata' in wine_dict:
            wine_dict['wine_metadata'] = wine_dict.pop('metadata')
        
        # Add user_id
        wine_dict['user_id'] = user_id
        
        db_wine = Wine(**wine_dict)
        
        self.db.add(db_wine)
        self.db.commit()
        self.db.refresh(db_wine)
        
        return db_wine
    
    def update(self, wine_id: str, user_id: str, wine_data: WineUpdate) -> Wine:
        """Update a wine entry"""
        db_wine = self.get_by_id(wine_id, user_id)
        
        if not db_wine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wine not found"
            )
        
        # Convert to dict and handle special fields
        update_data = wine_data.model_dump(exclude_unset=True)
        
        # Handle metadata/wine_metadata field renaming
        if 'metadata' in update_data:
            update_data['wine_metadata'] = update_data.pop('metadata')
        
        # If storage is being changed, validate it exists and belongs to user
        if 'storage_id' in update_data:
            storage = self.db.query(Storage).filter(
                Storage.id == update_data['storage_id'],
                Storage.user_id == user_id
            ).first()
            
            if not storage:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Storage not found"
                )
        else:
            # Use existing storage
            storage = db_wine.storage
        
        # If position is being updated, validate it
        if 'position' in update_data:
            position = update_data['position']
            
            if position:
                if not PositionValidator.validate_position(position, storage):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid position for this storage configuration"
                    )
                
                # Check if position is already occupied (excluding this wine)
                if PositionValidator.is_position_occupied(
                    position, 
                    storage.id, 
                    self.db, 
                    wine_id=wine_id
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Position already occupied by another wine"
                    )
        
        # Update wine attributes
        for key, value in update_data.items():
            setattr(db_wine, key, value)
        
        self.db.commit()
        self.db.refresh(db_wine)
        
        return db_wine
    
    def delete(self, wine_id: str, user_id: str) -> bool:
        """Delete a wine entry"""
        db_wine = self.get_by_id(wine_id, user_id)
        
        if not db_wine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wine not found"
            )
        
        self.db.delete(db_wine)
        self.db.commit()
        
        return True