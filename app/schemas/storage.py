from typing import Dict, Optional
from pydantic import BaseModel, Field

class StorageBase(BaseModel):
    name: str
    type: str
    dimensions: Dict
    total_positions: int
    position_naming_scheme: str
    
class StorageCreate(StorageBase):
    pass

class StorageUpdate(StorageBase):
    name: Optional[str] = None
    type: Optional[str] = None
    dimensions: Optional[Dict] = None
    total_positions: Optional[int] = None
    position_naming_scheme: Optional[str] = None
    
class StorageInDB(StorageBase):
    id: str
    user_id: str
    
    class Config:
        from_attributes = True