"""
Endpoints pour la gestion des utilisateurs (admin uniquement).
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.db.models.user import User, UserRole
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.schemas.common import PaginatedResponse, MessageResponse
from app.api.deps import get_current_active_user, require_admin
from app.crud import user as crud_user


router = APIRouter()


@router.get("", response_model=PaginatedResponse[UserResponse])
def list_users(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre d'éléments à retourner"),
    search: Optional[str] = Query(None, description="Recherche dans email ou username"),
    role: Optional[UserRole] = Query(None, description="Filtrer par rôle"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif/inactif"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Liste tous les utilisateurs avec pagination et filtres (admin uniquement).
    """
    users = crud_user.get_users(
        db,
        skip=skip,
        limit=limit,
        search=search,
        role=role,
        is_active=is_active
    )
    
    total = crud_user.count_users(
        db,
        search=search,
        role=role,
        is_active=is_active
    )
    
    return PaginatedResponse(
        items=users,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Récupère un utilisateur par son ID (admin uniquement).
    """
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return user


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Crée un nouvel utilisateur (admin uniquement).
    """
    # Vérifier si l'email existe déjà
    if crud_user.get_user_by_email(db, user_in.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec cet email existe déjà"
        )
    
    # Vérifier si le username existe déjà
    if crud_user.get_user_by_username(db, user_in.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un utilisateur avec ce nom d'utilisateur existe déjà"
        )
    
    return crud_user.create_user(db, user_in)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Met à jour un utilisateur (admin uniquement).
    """
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Vérifier les conflits d'email
    if user_update.email and user_update.email != user.email:
        existing = crud_user.get_user_by_email(db, user_update.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )
    
    # Vérifier les conflits de username
    if user_update.username and user_update.username != user.username:
        existing = crud_user.get_user_by_username(db, user_update.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec ce nom d'utilisateur existe déjà"
            )
    
    updated_user = crud_user.update_user(db, user_id, user_update)
    return updated_user


@router.post("/{user_id}/activate", response_model=MessageResponse)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Active un utilisateur (admin uniquement).
    """
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur est déjà actif"
        )
    
    user_update = UserUpdate(is_active=True)
    crud_user.update_user(db, user_id, user_update)
    
    return MessageResponse(message=f"Utilisateur {user.username} activé avec succès")


@router.post("/{user_id}/deactivate", response_model=MessageResponse)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Désactive un utilisateur (admin uniquement).
    """
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Empêcher l'admin de se désactiver lui-même
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas désactiver votre propre compte"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="L'utilisateur est déjà inactif"
        )
    
    user_update = UserUpdate(is_active=False)
    crud_user.update_user(db, user_id, user_update)
    
    return MessageResponse(message=f"Utilisateur {user.username} désactivé avec succès")


@router.delete("/{user_id}", response_model=MessageResponse)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Supprime un utilisateur (admin uniquement).
    """
    user = crud_user.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    # Empêcher l'admin de se supprimer lui-même
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas supprimer votre propre compte"
        )
    
    crud_user.delete_user(db, user_id)
    
    return MessageResponse(message=f"Utilisateur {user.username} supprimé avec succès")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère les informations de l'utilisateur connecté.
    """
    return current_user
