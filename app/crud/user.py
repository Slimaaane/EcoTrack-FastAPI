"""
Module CRUD pour la gestion des utilisateurs.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Récupère un utilisateur par son ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Récupère un utilisateur par son email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Récupère un utilisateur par son nom d'utilisateur."""
    return db.query(User).filter(User.username == username).first()


def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None
) -> List[User]:
    """
    Récupère une liste paginée d'utilisateurs avec filtres optionnels.
    
    Args:
        db: Session de base de données
        skip: Nombre d'éléments à sauter (pagination)
        limit: Nombre maximum d'éléments à retourner
        search: Recherche dans email ou username
        role: Filtrer par rôle
        is_active: Filtrer par statut actif/inactif
    """
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.email.contains(search),
                User.username.contains(search)
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()


def count_users(
    db: Session,
    search: Optional[str] = None,
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None
) -> int:
    """Compte le nombre total d'utilisateurs avec filtres."""
    query = db.query(User)
    
    if search:
        query = query.filter(
            or_(
                User.email.contains(search),
                User.username.contains(search)
            )
        )
    
    if role:
        query = query.filter(User.role == role)
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    return query.count()


def create_user(db: Session, user: UserCreate) -> User:
    """Crée un nouvel utilisateur."""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        role=user.role if user.role else UserRole.USER,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
    """
    Met à jour un utilisateur existant.
    
    Args:
        db: Session de base de données
        user_id: ID de l'utilisateur à modifier
        user_update: Données de mise à jour
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Si un nouveau mot de passe est fourni, le hasher
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Supprime un utilisateur."""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authentifie un utilisateur avec son username et mot de passe.
    
    Returns:
        L'utilisateur si les credentials sont valides, None sinon
    """
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
