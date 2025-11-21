"""
Endpoints pour la gestion des sources de données.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.source import SourceResponse, SourceCreate, SourceUpdate
from app.schemas.common import PaginatedResponse, MessageResponse
from app.api.deps import get_current_active_user, require_admin
from app.crud import source as crud_source


router = APIRouter()


@router.get("", response_model=PaginatedResponse[SourceResponse])
def list_sources(
    skip: int = Query(0, ge=0, description="Nombre d'éléments à sauter"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre d'éléments à retourner"),
    search: Optional[str] = Query(None, description="Recherche dans nom ou description"),
    format: Optional[str] = Query(None, description="Filtrer par format (JSON, CSV, XML)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Liste toutes les sources avec pagination et filtres.
    """
    sources = crud_source.get_sources(
        db,
        skip=skip,
        limit=limit,
        search=search,
        format=format
    )
    
    total = crud_source.count_sources(
        db,
        search=search,
        format=format
    )
    
    return PaginatedResponse(
        items=sources,
        total=total,
        skip=skip,
        limit=limit,
        has_more=(skip + len(sources)) < total
    )


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère une source par son ID.
    """
    source = crud_source.get_source(db, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source non trouvée"
        )
    return source


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
def create_source(
    source_in: SourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Crée une nouvelle source (admin uniquement).
    """
    # Vérifier si le nom existe déjà
    if crud_source.get_source_by_name(db, source_in.name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Une source avec ce nom existe déjà"
        )
    
    return crud_source.create_source(db, source_in)


@router.patch("/{source_id}", response_model=SourceResponse)
def update_source(
    source_id: int,
    source_update: SourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Met à jour une source (admin uniquement).
    """
    source = crud_source.get_source(db, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source non trouvée"
        )
    
    # Vérifier les conflits de nom
    if source_update.name and source_update.name != source.name:
        existing = crud_source.get_source_by_name(db, source_update.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une source avec ce nom existe déjà"
            )
    
    updated_source = crud_source.update_source(db, source_id, source_update)
    return updated_source


@router.delete("/{source_id}", response_model=MessageResponse)
def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Supprime une source (admin uniquement).
    
    Note: Supprime également tous les indicateurs associés (cascade).
    """
    source = crud_source.get_source(db, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source non trouvée"
        )
    
    crud_source.delete_source(db, source_id)
    
    return MessageResponse(message=f"Source '{source.name}' supprimée avec succès")
