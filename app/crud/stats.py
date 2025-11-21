"""
Module pour les statistiques et agrégations d'indicateurs.
"""
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime

from app.db.models.indicator import Indicator


def get_average_by_type(
    db: Session,
    type: str,
    zone_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> Optional[float]:
    """
    Calcule la moyenne des valeurs pour un type d'indicateur donné.
    
    Args:
        db: Session de base de données
        type: Type d'indicateur
        zone_id: Filtrer par zone (optionnel)
        from_date: Date de début (optionnel)
        to_date: Date de fin (optionnel)
    
    Returns:
        Moyenne des valeurs ou None si aucune donnée
    """
    query = db.query(func.avg(Indicator.value)).filter(Indicator.type == type)
    
    if zone_id:
        query = query.filter(Indicator.zone_id == zone_id)
    
    if from_date:
        query = query.filter(Indicator.timestamp >= from_date)
    
    if to_date:
        query = query.filter(Indicator.timestamp <= to_date)
    
    result = query.scalar()
    return float(result) if result else None


def get_stats_by_type(
    db: Session,
    type: str,
    zone_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Calcule des statistiques complètes pour un type d'indicateur.
    
    Returns:
        Dictionnaire avec min, max, avg, count
    """
    query = db.query(
        func.min(Indicator.value),
        func.max(Indicator.value),
        func.avg(Indicator.value),
        func.count(Indicator.id)
    ).filter(Indicator.type == type)
    
    if zone_id:
        query = query.filter(Indicator.zone_id == zone_id)
    
    if from_date:
        query = query.filter(Indicator.timestamp >= from_date)
    
    if to_date:
        query = query.filter(Indicator.timestamp <= to_date)
    
    result = query.first()
    
    if result and result[3] > 0:  # Si count > 0
        return {
            "min": float(result[0]) if result[0] else None,
            "max": float(result[1]) if result[1] else None,
            "avg": float(result[2]) if result[2] else None,
            "count": result[3]
        }
    
    return {"min": None, "max": None, "avg": None, "count": 0}


def get_stats_by_zone(
    db: Session,
    zone_id: int,
    type: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Calcule des statistiques groupées par type pour une zone donnée.
    
    Returns:
        Liste de dictionnaires avec type, min, max, avg, count
    """
    query = db.query(
        Indicator.type,
        func.min(Indicator.value).label('min'),
        func.max(Indicator.value).label('max'),
        func.avg(Indicator.value).label('avg'),
        func.count(Indicator.id).label('count')
    ).filter(Indicator.zone_id == zone_id)
    
    if type:
        query = query.filter(Indicator.type == type)
    
    if from_date:
        query = query.filter(Indicator.timestamp >= from_date)
    
    if to_date:
        query = query.filter(Indicator.timestamp <= to_date)
    
    query = query.group_by(Indicator.type)
    
    results = query.all()
    
    return [
        {
            "type": row[0],
            "min": float(row[1]) if row[1] else None,
            "max": float(row[2]) if row[2] else None,
            "avg": float(row[3]) if row[3] else None,
            "count": row[4]
        }
        for row in results
    ]


def get_trend_data(
    db: Session,
    type: str,
    zone_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Récupère les données de tendance (évolution temporelle) pour un type d'indicateur.
    
    Returns:
        Liste de points (timestamp, value) ordonnés par date
    """
    query = db.query(
        Indicator.timestamp,
        func.avg(Indicator.value).label('avg_value')
    ).filter(Indicator.type == type)
    
    if zone_id:
        query = query.filter(Indicator.zone_id == zone_id)
    
    if from_date:
        query = query.filter(Indicator.timestamp >= from_date)
    
    if to_date:
        query = query.filter(Indicator.timestamp <= to_date)
    
    # Grouper par timestamp (ou par jour selon les besoins)
    query = query.group_by(Indicator.timestamp).order_by(Indicator.timestamp.asc()).limit(limit)
    
    results = query.all()
    
    return [
        {
            "timestamp": row[0].isoformat(),
            "value": float(row[1]) if row[1] else None
        }
        for row in results
    ]


def get_comparison_by_zones(
    db: Session,
    type: str,
    zone_ids: List[int],
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Compare les moyennes d'un type d'indicateur entre plusieurs zones.
    
    Args:
        db: Session de base de données
        type: Type d'indicateur
        zone_ids: Liste des IDs de zones à comparer
        from_date: Date de début (optionnel)
        to_date: Date de fin (optionnel)
    
    Returns:
        Liste de dictionnaires avec zone_id et avg
    """
    query = db.query(
        Indicator.zone_id,
        func.avg(Indicator.value).label('avg_value'),
        func.count(Indicator.id).label('count')
    ).filter(
        and_(
            Indicator.type == type,
            Indicator.zone_id.in_(zone_ids)
        )
    )
    
    if from_date:
        query = query.filter(Indicator.timestamp >= from_date)
    
    if to_date:
        query = query.filter(Indicator.timestamp <= to_date)
    
    query = query.group_by(Indicator.zone_id)
    
    results = query.all()
    
    return [
        {
            "zone_id": row[0],
            "avg": float(row[1]) if row[1] else None,
            "count": row[2]
        }
        for row in results
    ]


def get_types_distribution(
    db: Session,
    zone_id: Optional[int] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None
) -> List[Dict[str, Any]]:
    """
    Récupère la distribution des types d'indicateurs (nombre par type).
    
    Returns:
        Liste de dictionnaires avec type et count
    """
    query = db.query(
        Indicator.type,
        func.count(Indicator.id).label('count')
    )
    
    if zone_id:
        query = query.filter(Indicator.zone_id == zone_id)
    
    if from_date:
        query = query.filter(Indicator.timestamp >= from_date)
    
    if to_date:
        query = query.filter(Indicator.timestamp <= to_date)
    
    query = query.group_by(Indicator.type).order_by(func.count(Indicator.id).desc())
    
    results = query.all()
    
    return [
        {
            "type": row[0],
            "count": row[1]
        }
        for row in results
    ]
