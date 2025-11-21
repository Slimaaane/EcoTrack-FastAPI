from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ZoneBase(BaseModel):
    """Schéma de base pour Zone."""
    name: str = Field(..., min_length=1, max_length=100, description="Nom de la zone")
    postal_code: Optional[str] = Field(None, max_length=20, description="Code postal")
    geom: Optional[str] = Field(None, description="Géométrie (JSON ou WKT)")
    description: Optional[str] = Field(None, description="Description de la zone")


class ZoneCreate(ZoneBase):
    """Schéma pour la création d'une zone."""
    pass


class ZoneUpdate(BaseModel):
    """Schéma pour la mise à jour d'une zone."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nouveau nom")
    postal_code: Optional[str] = Field(None, max_length=20, description="Nouveau code postal")
    geom: Optional[str] = Field(None, description="Nouvelle géométrie")
    description: Optional[str] = Field(None, description="Nouvelle description")


class ZoneResponse(ZoneBase):
    """Schéma de réponse pour Zone."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)
