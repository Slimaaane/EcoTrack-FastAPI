"""
Module CRUD pour la gestion des sources de données.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate


def get_source(db: Session, source_id: int) -> Optional[Source]:
    """Récupère une source par son ID."""
    return db.query(Source).filter(Source.id == source_id).first()


def get_source_by_name(db: Session, name: str) -> Optional[Source]:
    """Récupère une source par son nom."""
    return db.query(Source).filter(Source.name == name).first()


def get_sources(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    format: Optional[str] = None
) -> List[Source]:
    """
    Récupère une liste paginée de sources avec filtres optionnels.
    
    Args:
        db: Session de base de données
        skip: Nombre d'éléments à sauter (pagination)
        limit: Nombre maximum d'éléments à retourner
        search: Recherche dans nom ou description
        format: Filtrer par format (JSON, CSV, XML, etc.)
    """
    query = db.query(Source)
    
    if search:
        query = query.filter(
            or_(
                Source.name.contains(search),
                Source.description.contains(search)
            )
        )
    
    if format:
        query = query.filter(Source.format == format)
    
    return query.offset(skip).limit(limit).all()


def count_sources(
    db: Session,
    search: Optional[str] = None,
    format: Optional[str] = None
) -> int:
    """Compte le nombre total de sources avec filtres."""
    query = db.query(Source)
    
    if search:
        query = query.filter(
            or_(
                Source.name.contains(search),
                Source.description.contains(search)
            )
        )
    
    if format:
        query = query.filter(Source.format == format)
    
    return query.count()


def create_source(db: Session, source: SourceCreate) -> Source:
    """Crée une nouvelle source."""
    db_source = Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def update_source(db: Session, source_id: int, source_update: SourceUpdate) -> Optional[Source]:
    """
    Met à jour une source existante.
    
    Args:
        db: Session de base de données
        source_id: ID de la source à modifier
        source_update: Données de mise à jour
    """
    db_source = get_source(db, source_id)
    if not db_source:
        return None
    
    update_data = source_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_source, field, value)
    
    db.commit()
    db.refresh(db_source)
    return db_source


def delete_source(db: Session, source_id: int) -> bool:
    """Supprime une source."""
    db_source = get_source(db, source_id)
    if not db_source:
        return False
    
    db.delete(db_source)
    db.commit()
    return True
