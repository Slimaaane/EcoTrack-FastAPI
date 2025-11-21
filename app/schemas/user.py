from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from app.db.models.user import UserRole


# Schémas de base
class UserBase(BaseModel):
    """Schéma de base pour User."""
    email: EmailStr = Field(..., description="Adresse email unique de l'utilisateur")
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur unique")


class UserCreate(UserBase):
    """Schéma pour la création d'un utilisateur."""
    password: str = Field(..., min_length=6, description="Mot de passe (min 6 caractères)")
    role: Optional[UserRole] = Field(default=UserRole.USER, description="Rôle de l'utilisateur")


class UserUpdate(BaseModel):
    """Schéma pour la mise à jour d'un utilisateur."""
    email: Optional[EmailStr] = Field(None, description="Nouvelle adresse email")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Nouveau nom d'utilisateur")
    password: Optional[str] = Field(None, min_length=6, description="Nouveau mot de passe")
    role: Optional[UserRole] = Field(None, description="Nouveau rôle")
    is_active: Optional[bool] = Field(None, description="Statut d'activation")


class UserResponse(UserBase):
    """Schéma de réponse pour User."""
    id: int
    role: UserRole
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Schéma interne incluant le mot de passe haché."""
    hashed_password: str
