"""
Endpoints pour les statistiques et agrégations d'indicateurs.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.db.session import get_db
from app.db.models.user import User
from app.api.deps import get_current_active_user
from app.crud import stats as crud_stats
from app.crud import zone as crud_zone


router = APIRouter()


@router.get("/average/{type}")
def get_average_by_type(
    type: str,
    zone_id: Optional[int] = Query(None, gt=0, description="Filtrer par zone"),
    from_date: Optional[datetime] = Query(None, description="Date de début"),
    to_date: Optional[datetime] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Calcule la moyenne des valeurs pour un type d'indicateur.
    
    Exemple: GET /stats/average/air_quality?zone_id=1&from_date=2025-01-01
    """
    avg = crud_stats.get_average_by_type(
        db,
        type=type,
        zone_id=zone_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "type": type,
        "zone_id": zone_id,
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None,
        "average": avg
    }


@router.get("/summary/{type}")
def get_stats_by_type(
    type: str,
    zone_id: Optional[int] = Query(None, gt=0, description="Filtrer par zone"),
    from_date: Optional[datetime] = Query(None, description="Date de début"),
    to_date: Optional[datetime] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Calcule des statistiques complètes (min, max, avg, count) pour un type d'indicateur.
    
    Exemple: GET /stats/summary/co2?zone_id=1
    """
    stats = crud_stats.get_stats_by_type(
        db,
        type=type,
        zone_id=zone_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "type": type,
        "zone_id": zone_id,
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None,
        **stats
    }


@router.get("/zone/{zone_id}")
def get_stats_by_zone(
    zone_id: int,
    type: Optional[str] = Query(None, description="Filtrer par type"),
    from_date: Optional[datetime] = Query(None, description="Date de début"),
    to_date: Optional[datetime] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Calcule des statistiques groupées par type pour une zone donnée.
    
    Retourne les min/max/avg/count pour chaque type d'indicateur dans la zone.
    """
    # Vérifier que la zone existe
    zone = crud_zone.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} non trouvée"
        )
    
    stats = crud_stats.get_stats_by_zone(
        db,
        zone_id=zone_id,
        type=type,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "zone_id": zone_id,
        "zone_name": zone.name,
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None,
        "statistics": stats
    }


@router.get("/trend/{type}")
def get_trend_data(
    type: str,
    zone_id: Optional[int] = Query(None, gt=0, description="Filtrer par zone"),
    from_date: Optional[datetime] = Query(None, description="Date de début"),
    to_date: Optional[datetime] = Query(None, description="Date de fin"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre de points"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Récupère les données de tendance (évolution temporelle) pour un type d'indicateur.
    
    Retourne une série temporelle des valeurs moyennes, utile pour afficher des graphiques.
    """
    trend = crud_stats.get_trend_data(
        db,
        type=type,
        zone_id=zone_id,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )
    
    return {
        "type": type,
        "zone_id": zone_id,
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None,
        "data_points": len(trend),
        "trend": trend
    }


@router.post("/compare-zones/{type}")
def compare_zones(
    type: str,
    zone_ids: List[int],
    from_date: Optional[datetime] = Query(None, description="Date de début"),
    to_date: Optional[datetime] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Compare les moyennes d'un type d'indicateur entre plusieurs zones.
    
    Body: Liste des IDs de zones à comparer
    Exemple: POST /stats/compare-zones/air_quality
    Body: [1, 2, 3]
    """
    if not zone_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La liste de zone_ids ne peut pas être vide"
        )
    
    # Vérifier que toutes les zones existent
    for zone_id in zone_ids:
        zone = crud_zone.get_zone(db, zone_id)
        if not zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Zone {zone_id} non trouvée"
            )
    
    comparison = crud_stats.get_comparison_by_zones(
        db,
        type=type,
        zone_ids=zone_ids,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "type": type,
        "zones_compared": len(zone_ids),
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None,
        "comparison": comparison
    }


@router.get("/distribution")
def get_types_distribution(
    zone_id: Optional[int] = Query(None, gt=0, description="Filtrer par zone"),
    from_date: Optional[datetime] = Query(None, description="Date de début"),
    to_date: Optional[datetime] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Récupère la distribution des types d'indicateurs (nombre par type).
    
    Utile pour afficher des graphiques en camembert ou en barres.
    """
    distribution = crud_stats.get_types_distribution(
        db,
        zone_id=zone_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return {
        "zone_id": zone_id,
        "from_date": from_date.isoformat() if from_date else None,
        "to_date": to_date.isoformat() if to_date else None,
        "total_types": len(distribution),
        "distribution": distribution
    }
