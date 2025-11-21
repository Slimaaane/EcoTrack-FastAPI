from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base


class Indicator(Base):
    """Modèle Indicator pour les indicateurs environnementaux."""
    
    __tablename__ = "indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(100), index=True, nullable=False)  # Ex: air_quality, co2, energy, waste
    name = Column(String(200), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)  # Ex: µg/m³, kg, kWh
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    meta_info = Column(Text, nullable=True)  # JSON pour données supplémentaires
    
    # Clés étrangères
    zone_id = Column(Integer, ForeignKey("zones.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, ForeignKey("sources.id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Relations
    zone = relationship("Zone", back_populates="indicators")
    source = relationship("Source", back_populates="indicators")
    owner = relationship("User", back_populates="indicators")
    
    # Index composites pour les requêtes fréquentes
    __table_args__ = (
        Index('idx_indicator_zone_type_timestamp', 'zone_id', 'type', 'timestamp'),
        Index('idx_indicator_type_timestamp', 'type', 'timestamp'),
    )
