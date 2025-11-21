"""
Endpoints pour la gestion des zones géographiques.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.zone import ZoneResponse, ZoneCreate, ZoneUpdate
from app.schemas.common import PaginatedResponse, MessageResponse
from app.api.deps import get_current_active_user, require_admin
from app.crud import zone as crud_zone


router = APIRouter()


@router.get("", response_model=PaginatedResponse[ZoneResponse])
def list_zones(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre d'éléments à retourner"),
    search: Optional[str] = Query(None, description="Recherche dans nom ou description"),
    postal_code: Optional[str] = Query(None, description="Filtrer par code postal"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Liste toutes les zones avec pagination et filtres.
    """
    zones = crud_zone.get_zones(
        db,
        skip=skip,
        limit=limit,
        search=search,
        postal_code=postal_code
    )
    
    total = crud_zone.count_zones(
        db,
        search=search,
        postal_code=postal_code
    )
    
    return PaginatedResponse(
        items=zones,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(zones)) < total
    )


@router.get("/{zone_id}", response_model=ZoneResponse)
def get_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère une zone par son ID.
    """
    zone = crud_zone.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone non trouvée"
        )
    return zone


@router.post("", response_model=ZoneResponse, status_code=status.HTTP_201_CREATED)
def create_zone(
    zone_in: ZoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Crée une nouvelle zone (admin uniquement).
    """
    # Vérifier si le nom existe déjà
    if crud_zone.get_zone_by_name(db, zone_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une zone avec ce nom existe déjà"
        )
    
    return crud_zone.create_zone(db, zone_in)


@router.patch("/{zone_id}", response_model=ZoneResponse)
def update_zone(
    zone_id: int,
    zone_update: ZoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Met à jour une zone (admin uniquement).
    """
    zone = crud_zone.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone non trouvée"
        )
    
    # Vérifier les conflits de nom
    if zone_update.name and zone_update.name != zone.name:
        existing = crud_zone.get_zone_by_name(db, zone_update.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une zone avec ce nom existe déjà"
            )
    
    updated_zone = crud_zone.update_zone(db, zone_id, zone_update)
    return updated_zone


@router.delete("/{zone_id}", response_model=MessageResponse)
def delete_zone(
    zone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Supprime une zone (admin uniquement).
    
    Note: Supprime également tous les indicateurs associés (cascade).
    """
    zone = crud_zone.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone non trouvée"
        )
    
    crud_zone.delete_zone(db, zone_id)
    
    return MessageResponse(message=f"Zone '{zone.name}' supprimée avec succès")
