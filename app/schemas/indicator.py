from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class IndicatorBase(BaseModel):
    """Schéma de base pour Indicator."""
    type: str = Field(..., min_length=1, max_length=100, description="Type d'indicateur (air_quality, co2, energy, waste)")
    name: str = Field(..., min_length=1, max_length=200, description="Nom de l'indicateur")
    value: float = Field(..., description="Valeur mesurée")
    unit: str = Field(..., min_length=1, max_length=50, description="Unité de mesure (µg/m³, kg, kWh)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Date et heure de la mesure")
    meta_info: Optional[str] = Field(None, description="Métadonnées supplémentaires (JSON)")
    zone_id: int = Field(..., gt=0, description="ID de la zone")
    source_id: int = Field(..., gt=0, description="ID de la source")


class IndicatorCreate(IndicatorBase):
    """Schéma pour la création d'un indicateur."""
    pass


class IndicatorBulkCreate(BaseModel):
    """Schéma pour l'insertion en lot d'indicateurs."""
    indicators: list[IndicatorCreate] = Field(..., min_length=1, description="Liste d'indicateurs à créer")


class IndicatorUpdate(BaseModel):
    """Schéma pour la mise à jour d'un indicateur."""
    type: Optional[str] = Field(None, min_length=1, max_length=100, description="Nouveau type")
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="Nouveau nom")
    value: Optional[float] = Field(None, description="Nouvelle valeur")
    unit: Optional[str] = Field(None, min_length=1, max_length=50, description="Nouvelle unité")
    timestamp: Optional[datetime] = Field(None, description="Nouvelle date/heure")
    meta_info: Optional[str] = Field(None, description="Nouvelles métadonnées")
    zone_id: Optional[int] = Field(None, gt=0, description="Nouvel ID de zone")
    source_id: Optional[int] = Field(None, gt=0, description="Nouvel ID de source")


class IndicatorResponse(IndicatorBase):
    """Schéma de réponse pour Indicator."""
    id: int
    owner_id: int
    
    model_config = ConfigDict(from_attributes=True)


class IndicatorQuery(BaseModel):
    """Schéma pour les filtres de recherche d'indicateurs."""
    type: Optional[str] = Field(None, description="Filtrer par type")
    zone_id: Optional[int] = Field(None, gt=0, description="Filtrer par zone")
    source_id: Optional[int] = Field(None, gt=0, description="Filtrer par source")
    from_date: Optional[datetime] = Field(None, description="Date de début")
    to_date: Optional[datetime] = Field(None, description="Date de fin")
    skip: int = Field(0, ge=0, description="Nombre d'éléments à sauter")
    limit: int = Field(100, ge=1, le=1000, description="Nombre max d'éléments à retourner")
    sort_by: Optional[str] = Field("timestamp", description="Champ de tri")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Ordre de tri")
