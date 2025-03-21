from typing import Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel

class WineBase(BaseModel):
    name: str

class WineCreate(WineBase):
    storage_id: str
    position: Optional[str] = None
    description: Optional[str] = None
    wine_metadata: Optional[Dict[str, Any]] = None

class WineUpdate(BaseModel):
    name: Optional[str] = None
    storage_id: Optional[str] = None
    position: Optional[str] = None
    description: Optional[str] = None
    wine_metadata: Optional[Dict[str, Any]] = None

class WineResponse(WineBase):
    id: str
    storage_id: str
    position: Optional[str] = None
    added_date: datetime
    label_image_url: Optional[str] = None
    description: Optional[str] = None
    wine_metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True