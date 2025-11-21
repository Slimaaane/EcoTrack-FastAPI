"""
Module CRUD pour la gestion des indicateurs environnementaux.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, asc
from datetime import datetime

from app.db.models.indicator import Indicator
from app.schemas.indicator import IndicatorCreate, IndicatorUpdate


def get_indicator(db: Session, indicator_id: int) -> Optional[Indicator]:
    """Récupère un indicateur par son ID."""
    return db.query(Indicator).filter(Indicator.id == indicator_id).first()


def get_indicators(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    zone_id: Optional[int] = None,
    source_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    sort_by: str = "timestamp",
    sort_order: str = "desc"
) -> List[Indicator]:
    """
    Récupère une liste paginée d'indicateurs avec filtres optionnels.
    
    Args:
        db: Session de base de données
        skip: Nombre d'éléments à sauter (pagination)
        limit: Nombre maximum d'éléments à retourner
        type: Filtrer par type d'indicateur
        zone_id: Filtrer par zone
        source_id: Filtrer par source
        owner_id: Filtrer par propriétaire
        from_date: Date de début
        to_date: Date de fin
        sort_by: Champ de tri (timestamp, value, type)
        sort_order: Ordre de tri (asc, desc)
    """
    query = db.query(Indicator)
    
    # Application des filtres
    filters = []
    
    if type:
        filters.append(Indicator.type == type)
    
    if zone_id:
        filters.append(Indicator.zone_id == zone_id)
    
    if source_id:
        filters.append(Indicator.source_id == source_id)
    
    if owner_id:
        filters.append(Indicator.owner_id == owner_id)
    
    if from_date:
        filters.append(Indicator.timestamp >= from_date)
    
    if to_date:
        filters.append(Indicator.timestamp <= to_date)
    
    if filters:
        query = query.filter(and_(*filters))
    
    # Tri
    sort_column = getattr(Indicator, sort_by, Indicator.timestamp)
    if sort_order == "asc":
        query = query.order_by(asc(sort_column))
    else:
        query = query.order_by(desc(sort_column))
    
    return query.offset(skip).limit(limit).all()


def count_indicators(
    db: Session,
    type: Optional[str] = None,
    zone_id: Optional[int] = None,
    source_id: Optional[int] = None,
    owner_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> int:
    """Compte le nombre total d'indicateurs avec filtres."""
    query = db.query(Indicator)
    
    filters = []
    
    if type:
        filters.append(Indicator.type == type)
    
    if zone_id:
        filters.append(Indicator.zone_id == zone_id)
    
    if source_id:
        filters.append(Indicator.source_id == source_id)
    
    if owner_id:
        filters.append(Indicator.owner_id == owner_id)
    
    if from_date:
        filters.append(Indicator.timestamp >= from_date)
    
    if to_date:
        filters.append(Indicator.timestamp <= to_date)
    
    if filters:
        query = query.filter(and_(*filters))
    
    return query.count()


def create_indicator(db: Session, indicator: IndicatorCreate, owner_id: int) -> Indicator:
    """Crée un nouvel indicateur."""
    db_indicator = Indicator(
        **indicator.model_dump(),
        owner_id=owner_id
    )
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)
    return db_indicator


def create_indicators_bulk(db: Session, indicators: List[IndicatorCreate], owner_id: int) -> List[Indicator]:
    """
    Crée plusieurs indicateurs en une seule transaction.
    
    Args:
        db: Session de base de données
        indicators: Liste d'indicateurs à créer
        owner_id: ID du propriétaire
        
    Returns:
        Liste des indicateurs créés
    """
    db_indicators = [
        Indicator(**indicator.model_dump(), owner_id=owner_id)
        for indicator in indicators
    ]
    
    db.add_all(db_indicators)
    db.commit()
    
    # Refresh tous les objets pour obtenir les IDs
    for db_indicator in db_indicators:
        db.refresh(db_indicator)
    
    return db_indicators


def update_indicator(db: Session, indicator_id: int, indicator_update: IndicatorUpdate) -> Optional[Indicator]:
    """
    Met à jour un indicateur existant.
    
    Args:
        db: Session de base de données
        indicator_id: ID de l'indicateur à modifier
        indicator_update: Données de mise à jour
    """
    db_indicator = get_indicator(db, indicator_id)
    if not db_indicator:
        return None
    
    update_data = indicator_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_indicator, field, value)
    
    db.commit()
    db.refresh(db_indicator)
    return db_indicator


def delete_indicator(db: Session, indicator_id: int) -> bool:
    """Supprime un indicateur."""
    db_indicator = get_indicator(db, indicator_id)
    if not db_indicator:
        return False
    
    db.delete(db_indicator)
    db.commit()
    return True


def delete_indicators_bulk(db: Session, indicator_ids: List[int]) -> int:
    """
    Supprime plusieurs indicateurs en une seule transaction.
    
    Args:
        db: Session de base de données
        indicator_ids: Liste des IDs à supprimer
        
    Returns:
        Nombre d'indicateurs supprimés
    """
    count = db.query(Indicator).filter(Indicator.id.in_(indicator_ids)).delete(synchronize_session=False)
    db.commit()
    return count
