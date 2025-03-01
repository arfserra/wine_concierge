import uuid
from sqlalchemy import Column, String, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.models.database import Base

class Storage(Base):
    __tablename__ = "storages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # wine_fridge, cellar, rack
    dimensions = Column(JSON, nullable=False)  # {"sections": 2, "rows": 6, "columns": 8}
    total_positions = Column(Integer, nullable=False)
    position_naming_scheme = Column(String, nullable=False)  # section-row-column
    user_id = Column(String, nullable=False)
    
    # Relationship - one storage can have many wines
    wines = relationship("Wine", back_populates="storage", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Storage(id='{self.id}', name='{self.name}', type='{self.type}')>"