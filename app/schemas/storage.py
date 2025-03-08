from typing import Dict, List, Optional
from pydantic import BaseModel, Field, computed_field

class StorageZone(BaseModel):
    name: str
    dimensions: Dict[str, int]
    temperature: Optional[float] = None
    humidity: Optional[float] = None

class StorageBase(BaseModel):
    name: str
    type: str
    zones: List[StorageZone]
    position_naming_scheme: str

class StorageCreate(StorageBase):
    @computed_field
    def total_positions(self) -> int:
        """Calculate total positions across all zones"""
        total = 0
        for zone in self.zones:
            # Calculate positions by multiplying dimensions
            positions = 1
            for dimension_value in zone.dimensions.values():
                positions *= dimension_value
            total += positions
        return total

class StorageUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    zones: Optional[List[StorageZone]] = None
    position_naming_scheme: Optional[str] = None

class StorageInDB(StorageBase):
    id: str
    user_id: str
    total_positions: int  # Regular field here, not computed
    
    class Config:
        from_attributes = True