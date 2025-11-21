"""
Endpoints pour la gestion des indicateurs environnementaux.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.indicator import (
    IndicatorResponse, 
    IndicatorCreate, 
    IndicatorUpdate,
    IndicatorBulkCreate
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.api.deps import get_current_active_user, require_admin
from app.crud import indicator as crud_indicator
from app.crud import zone as crud_zone
from app.crud import source as crud_source


router = APIRouter()


@router.get("", response_model=PaginatedResponse[IndicatorResponse])
def list_indicators(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre d'éléments à retourner"),
    type: Optional[str] = Query(None, description="Filtrer par type (air_quality, co2, energy, waste)"),
    zone_id: Optional[int] = Query(None, gt=0, description="Filtrer par zone"),
    source_id: Optional[int] = Query(None, gt=0, description="Filtrer par source"),
    from_date: Optional[datetime] = Query(None, description="Date de début (ISO 8601)"),
    to_date: Optional[datetime] = Query(None, description="Date de fin (ISO 8601)"),
    sort_by: str = Query("timestamp", description="Champ de tri (timestamp, value, type)"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Ordre de tri"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Liste tous les indicateurs avec pagination et filtres avancés.
    
    Filtres disponibles:
    - type: Type d'indicateur (air_quality, co2, energy, waste, etc.)
    - zone_id: ID de la zone géographique
    - source_id: ID de la source de données
    - from_date / to_date: Plage de dates
    - sort_by: Champ de tri (timestamp, value, type)
    - sort_order: asc ou desc
    """
    indicators = crud_indicator.get_indicators(
        db,
        skip=skip,
        limit=limit,
        type=type,
        zone_id=zone_id,
        source_id=source_id,
        from_date=from_date,
        to_date=to_date,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total = crud_indicator.count_indicators(
        db,
        type=type,
        zone_id=zone_id,
        source_id=source_id,
        from_date=from_date,
        to_date=to_date
    )
    
    return PaginatedResponse(
        items=indicators,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(indicators)) < total
    )


@router.get("/my", response_model=PaginatedResponse[IndicatorResponse])
def list_my_indicators(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre d'éléments à retourner"),
    type: Optional[str] = Query(None, description="Filtrer par type"),
    zone_id: Optional[int] = Query(None, gt=0, description="Filtrer par zone"),
    from_date: Optional[datetime] = Query(None, description="Date de début"),
    to_date: Optional[datetime] = Query(None, description="Date de fin"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Liste les indicateurs créés par l'utilisateur connecté.
    """
    indicators = crud_indicator.get_indicators(
        db,
        skip=skip,
        limit=limit,
        type=type,
        zone_id=zone_id,
        owner_id=current_user.id,
        from_date=from_date,
        to_date=to_date
    )
    
    total = crud_indicator.count_indicators(
        db,
        type=type,
        zone_id=zone_id,
        owner_id=current_user.id,
        from_date=from_date,
        to_date=to_date
    )
    
    return PaginatedResponse(
        items=indicators,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{indicator_id}", response_model=IndicatorResponse)
def get_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère un indicateur par son ID.
    """
    indicator = crud_indicator.get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicateur non trouvé"
        )
    return indicator


@router.post("", response_model=IndicatorResponse, status_code=status.HTTP_201_CREATED)
def create_indicator(
    indicator_in: IndicatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crée un nouvel indicateur.
    
    Vérifie que la zone et la source existent.
    """
    # Vérifier que la zone existe
    zone = crud_zone.get_zone(db, indicator_in.zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Zone {indicator_in.zone_id} non trouvée"
        )
    
    # Vérifier que la source existe
    source = crud_source.get_source(db, indicator_in.source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source {indicator_in.source_id} non trouvée"
        )
    
    return crud_indicator.create_indicator(db, indicator_in, current_user.id)


@router.post("/bulk", response_model=List[IndicatorResponse], status_code=status.HTTP_201_CREATED)
def create_indicators_bulk(
    bulk_data: IndicatorBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Crée plusieurs indicateurs en une seule requête (bulk insert).
    
    Optimisé pour l'ingestion de données en masse.
    Vérifie que toutes les zones et sources existent avant l'insertion.
    """
    # Extraire tous les zone_ids et source_ids uniques
    zone_ids = set(ind.zone_id for ind in bulk_data.indicators)
    source_ids = set(ind.source_id for ind in bulk_data.indicators)
    
    # Vérifier que toutes les zones existent
    for zone_id in zone_ids:
        if not crud_zone.get_zone(db, zone_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Zone {zone_id} non trouvée"
            )
    
    # Vérifier que toutes les sources existent
    for source_id in source_ids:
        if not crud_source.get_source(db, source_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source {source_id} non trouvée"
            )
    
    return crud_indicator.create_indicators_bulk(db, bulk_data.indicators, current_user.id)


@router.patch("/{indicator_id}", response_model=IndicatorResponse)
def update_indicator(
    indicator_id: int,
    indicator_update: IndicatorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Met à jour un indicateur.
    
    Un utilisateur peut modifier uniquement ses propres indicateurs.
    Les admins peuvent modifier n'importe quel indicateur.
    """
    indicator = crud_indicator.get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicateur non trouvé"
        )
    
    # Vérifier les permissions
    from app.db.models.user import UserRole
    if indicator.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez modifier que vos propres indicateurs"
        )
    
    # Vérifier la nouvelle zone si fournie
    if indicator_update.zone_id and indicator_update.zone_id != indicator.zone_id:
        if not crud_zone.get_zone(db, indicator_update.zone_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Zone {indicator_update.zone_id} non trouvée"
            )
    
    # Vérifier la nouvelle source si fournie
    if indicator_update.source_id and indicator_update.source_id != indicator.source_id:
        if not crud_source.get_source(db, indicator_update.source_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source {indicator_update.source_id} non trouvée"
            )
    
    updated_indicator = crud_indicator.update_indicator(db, indicator_id, indicator_update)
    return updated_indicator


@router.delete("/{indicator_id}", response_model=MessageResponse)
def delete_indicator(
    indicator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Supprime un indicateur.
    
    Un utilisateur peut supprimer uniquement ses propres indicateurs.
    Les admins peuvent supprimer n'importe quel indicateur.
    """
    indicator = crud_indicator.get_indicator(db, indicator_id)
    if not indicator:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indicateur non trouvé"
        )
    
    # Vérifier les permissions
    from app.db.models.user import UserRole
    if indicator.owner_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez supprimer que vos propres indicateurs"
        )
    
    crud_indicator.delete_indicator(db, indicator_id)
    
    return MessageResponse(message=f"Indicateur {indicator_id} supprimé avec succès")


@router.post("/bulk-delete", response_model=MessageResponse)
def delete_indicators_bulk(
    indicator_ids: List[int],
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Supprime plusieurs indicateurs en une seule requête (admin uniquement).
    
    Utile pour le nettoyage de données en masse.
    """
    count = crud_indicator.delete_indicators_bulk(db, indicator_ids)
    
    return MessageResponse(message=f"{count} indicateur(s) supprimé(s) avec succès")
