from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional, Any
from datetime import datetime

# Type générique pour les réponses paginées
T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """Schéma générique pour les réponses paginées."""
    items: list[T] = Field(..., description="Liste des éléments")
    total: int = Field(..., ge=0, description="Nombre total d'éléments")
    skip: int = Field(..., ge=0, description="Nombre d'éléments sautés")
    limit: int = Field(..., ge=1, description="Nombre max d'éléments par page")
    has_more: bool = Field(..., description="Indique s'il y a plus d'éléments")


class ErrorResponse(BaseModel):
    """Schéma pour les messages d'erreur."""
    detail: str = Field(..., description="Message d'erreur détaillé")
    error_code: Optional[str] = Field(None, description="Code d'erreur")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Horodatage de l'erreur")


class MessageResponse(BaseModel):
    """Schéma pour les messages de succès."""
    message: str = Field(..., description="Message de confirmation")
    data: Optional[Any] = Field(None, description="Données supplémentaires")


class StatsResponse(BaseModel):
    """Schéma pour les réponses de statistiques."""
    labels: list[str] = Field(..., description="Labels pour les graphiques")
    values: list[float] = Field(..., description="Valeurs correspondantes")
    metadata: Optional[dict] = Field(None, description="Métadonnées supplémentaires")
