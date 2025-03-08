import uuid
import datetime
from sqlalchemy import Column, String, Integer, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.models.database import Base

class Wine(Base):
    __tablename__ = "wines"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    producer = Column(String)
    vintage = Column(Integer)
    region = Column(String)
    country = Column(String)
    varietal = Column(JSON)  # List of varietals
    type = Column(String)  # Red, White, Rosé, Sparkling
    alcohol_percentage = Column(Float)
    label_image_url = Column(String)
    
    # Location information
    storage_id = Column(String, ForeignKey("storages.id"))
    position = Column(String)  # Now in format like "Red Zone-A3" or "White Zone-B2"
    added_date = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Rename metadata to wine_metadata to avoid conflict with SQLAlchemy's reserved name
    wine_metadata = Column(JSON)  # Additional information like scan confidence
    
    # Relationships
    storage = relationship("Storage", back_populates="wines")
    user_id = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<Wine(id='{self.id}', name='{self.name}', vintage='{self.vintage}')>"