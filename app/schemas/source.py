from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional


class SourceBase(BaseModel):
    """Schéma de base pour Source."""
    name: str = Field(..., min_length=1, max_length=100, description="Nom de la source")
    url: Optional[str] = Field(None, max_length=500, description="URL de la source")
    format: Optional[str] = Field(None, max_length=50, description="Format des données (JSON, CSV, XML)")
    frequency: Optional[str] = Field(None, max_length=50, description="Fréquence de mise à jour (daily, hourly, real-time)")
    limitations: Optional[str] = Field(None, description="Limitations connues (quotas, disponibilité)")
    description: Optional[str] = Field(None, description="Description de la source")


class SourceCreate(SourceBase):
    """Schéma pour la création d'une source."""
    pass


class SourceUpdate(BaseModel):
    """Schéma pour la mise à jour d'une source."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nouveau nom")
    url: Optional[str] = Field(None, max_length=500, description="Nouvelle URL")
    format: Optional[str] = Field(None, max_length=50, description="Nouveau format")
    frequency: Optional[str] = Field(None, max_length=50, description="Nouvelle fréquence")
    limitations: Optional[str] = Field(None, description="Nouvelles limitations")
    description: Optional[str] = Field(None, description="Nouvelle description")


class SourceResponse(SourceBase):
    """Schéma de réponse pour Source."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)
