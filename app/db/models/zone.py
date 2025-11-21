from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Zone(Base):
    """Modèle Zone pour les zones géographiques."""
    
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    postal_code = Column(String(20), index=True, nullable=True)
    geom = Column(Text, nullable=True)  # Stockage JSON ou WKT pour la géométrie
    description = Column(Text, nullable=True)
    
    # Relations
    indicators = relationship("Indicator", back_populates="zone", cascade="all, delete-orphan")
