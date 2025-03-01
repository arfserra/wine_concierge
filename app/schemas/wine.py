from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class WineBase(BaseModel):
    name: str
    producer: Optional[str] = None
    vintage: Optional[int] = None
    region: Optional[str] = None
    country: Optional[str] = None
    varietal: Optional[List[str]] = None
    type: Optional[str] = None
    alcohol_percentage: Optional[float] = None

class WineCreate(WineBase):
    storage_id: str
    position: Optional[str] = None
    label_image_url: Optional[str] = None
    metadata: Optional[Dict] = None

class WineUpdate(BaseModel):
    name: Optional[str] = None
    producer: Optional[str] = None
    vintage: Optional[int] = None
    region: Optional[str] = None
    country: Optional[str] = None
    varietal: Optional[List[str]] = None
    type: Optional[str] = None
    alcohol_percentage: Optional[float] = None
    storage_id: Optional[str] = None
    position: Optional[str] = None
    metadata: Optional[Dict] = None

class WineInDB(WineBase):
    id: str
    storage_id: str
    position: Optional[str] = None
    added_date: datetime
    label_image_url: Optional[str] = None
    metadata: Optional[Dict] = None
    user_id: str
    
    class Config:
        from_attributes = True