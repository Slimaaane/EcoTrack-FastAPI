from pydantic import BaseModel, Field
from typing import Optional
from app.db.models.user import UserRole


class Token(BaseModel):
    """Schéma pour le token JWT."""
    access_token: str = Field(..., description="Token JWT")
    token_type: str = Field(default="bearer", description="Type de token")


class TokenData(BaseModel):
    """Schéma pour les données contenues dans le token."""
    username: Optional[str] = Field(None, description="Nom d'utilisateur")
    role: Optional[UserRole] = Field(None, description="Rôle de l'utilisateur")


class LoginRequest(BaseModel):
    """Schéma pour la requête de connexion."""
    username: str = Field(..., description="Nom d'utilisateur ou email")
    password: str = Field(..., description="Mot de passe")
