from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from app.db.base import Base


class Source(Base):
    """Modèle Source pour les sources de données externes."""
    
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    url = Column(String(500), nullable=True)
    format = Column(String(50), nullable=True)  # Ex: JSON, CSV, XML
    frequency = Column(String(50), nullable=True)  # Ex: daily, hourly, real-time
    limitations = Column(Text, nullable=True)  # Description des limitations (quotas, etc.)
    description = Column(Text, nullable=True)
    
    # Relations
    indicators = relationship("Indicator", back_populates="source", cascade="all, delete-orphan")
