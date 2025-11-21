"""
Module CRUD pour la gestion des zones.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db.models.zone import Zone
from app.schemas.zone import ZoneCreate, ZoneUpdate


def get_zone(db: Session, zone_id: int) -> Optional[Zone]:
    """Récupère une zone par son ID."""
    return db.query(Zone).filter(Zone.id == zone_id).first()


def get_zone_by_name(db: Session, name: str) -> Optional[Zone]:
    """Récupère une zone par son nom."""
    return db.query(Zone).filter(Zone.name == name).first()


def get_zones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    postal_code: Optional[str] = None
) -> List[Zone]:
    """
    Récupère une liste paginée de zones avec filtres optionnels.
    
    Args:
        db: Session de base de données
        skip: Nombre d'éléments à sauter (pagination)
        limit: Nombre maximum d'éléments à retourner
        search: Recherche dans nom ou description
        postal_code: Filtrer par code postal
    """
    query = db.query(Zone)
    
    if search:
        query = query.filter(
            or_(
                Zone.name.contains(search),
                Zone.description.contains(search)
            )
        )
    
    if postal_code:
        query = query.filter(Zone.postal_code == postal_code)
    
    return query.offset(skip).limit(limit).all()


def count_zones(
    db: Session,
    search: Optional[str] = None,
    postal_code: Optional[str] = None
) -> int:
    """Compte le nombre total de zones avec filtres."""
    query = db.query(Zone)
    
    if search:
        query = query.filter(
            or_(
                Zone.name.contains(search),
                Zone.description.contains(search)
            )
        )
    
    if postal_code:
        query = query.filter(Zone.postal_code == postal_code)
    
    return query.count()


def create_zone(db: Session, zone: ZoneCreate) -> Zone:
    """Crée une nouvelle zone."""
    db_zone = Zone(**zone.model_dump())
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone


def update_zone(db: Session, zone_id: int, zone_update: ZoneUpdate) -> Optional[Zone]:
    """
    Met à jour une zone existante.
    
    Args:
        db: Session de base de données
        zone_id: ID de la zone à modifier
        zone_update: Données de mise à jour
    """
    db_zone = get_zone(db, zone_id)
    if not db_zone:
        return None
    
    update_data = zone_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_zone, field, value)
    
    db.commit()
    db.refresh(db_zone)
    return db_zone


def delete_zone(db: Session, zone_id: int) -> bool:
    """Supprime une zone."""
    db_zone = get_zone(db, zone_id)
    if not db_zone:
        return False
    
    db.delete(db_zone)
    db.commit()
    return True
