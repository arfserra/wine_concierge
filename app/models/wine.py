import uuid
import datetime
from sqlalchemy import Column, String, Integer, JSON, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.models.database import Base

class Wine(Base):
    __tablename__ = "wines"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic wine information
    name = Column(String, nullable=False)
    
    # Storage location information
    storage_id = Column(String, ForeignKey("storages.id"))
    position = Column(String)  # Position within the storage (e.g., "A3", "Red Zone-B2")
    added_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # AI analyzed information
    label_image_url = Column(String)  # Path to the stored label image
    description = Column(Text)  # Full text description from OpenAI analysis
    wine_metadata = Column(JSON)  # All wine metadata in a single JSON field
    
    # Relationship with storage
    storage = relationship("Storage", back_populates="wines")
    
    def __repr__(self):
        return f"<Wine(id='{self.id}', name='{self.name}')>"