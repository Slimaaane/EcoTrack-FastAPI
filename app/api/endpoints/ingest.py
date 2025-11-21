"""
Endpoints pour l'ingestion de données externes.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List
import httpx

from app.db.session import get_db
from app.db.models.user import User
from app.schemas.common import MessageResponse
from app.api.deps import get_current_active_user
from app.services.openaq import OpenAQService
from app.services.openmeteo import OpenMeteoService
from app.crud import indicator as crud_indicator
from app.crud import zone as crud_zone
from app.crud import source as crud_source


router = APIRouter()


@router.post("/openaq/latest", response_model=MessageResponse)
async def ingest_openaq_latest(
    zone_id: int = Query(..., gt=0, description="ID de la zone cible"),
    source_id: int = Query(..., gt=0, description="ID de la source OpenAQ"),
    country: str = Query("FR", description="Code pays ISO (FR, US, GB, etc.)"),
    city: Optional[str] = Query(None, description="Nom de la ville"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre de mesures à récupérer"),
    api_key: Optional[str] = Query(None, description="Clé API OpenAQ (optionnelle)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ingère les dernières mesures de qualité de l'air depuis OpenAQ.
    
    Récupère les données de pollution (PM2.5, PM10, O3, NO2, SO2, CO)
    et les insère comme indicateurs dans la base de données.
    
    Exemple: POST /ingest/openaq/latest?zone_id=1&source_id=1&country=FR&city=Paris
    """
    # Vérifier que la zone existe
    zone = crud_zone.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} non trouvée"
        )
    
    # Vérifier que la source existe
    source = crud_source.get_source(db, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} non trouvée"
        )
    
    try:
        # Récupérer et transformer les données
        openaq = OpenAQService(api_key=api_key)
        indicators = await openaq.fetch_and_transform(
            zone_id=zone_id,
            source_id=source_id,
            country=country,
            city=city,
            limit=limit
        )
        
        if not indicators:
            return MessageResponse(
                message="Aucune donnée disponible pour les paramètres spécifiés"
            )
        
        # Insérer en bulk
        created = crud_indicator.create_indicators_bulk(db, indicators, current_user.id)
        
        return MessageResponse(
            message=f"{len(created)} indicateurs OpenAQ insérés avec succès"
        )
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la récupération des données OpenAQ: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue: {str(e)}"
        )


@router.post("/openmeteo/weather", response_model=MessageResponse)
async def ingest_openmeteo_weather(
    zone_id: int = Query(..., gt=0, description="ID de la zone cible"),
    source_id: int = Query(..., gt=0, description="ID de la source Open-Meteo"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    location_name: str = Query("Unknown", description="Nom de la localisation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ingère les données météorologiques actuelles depuis Open-Meteo.
    
    Récupère température, humidité, précipitations, vent, etc.
    
    Exemple: POST /ingest/openmeteo/weather?zone_id=1&source_id=2&latitude=48.8566&longitude=2.3522&location_name=Paris
    """
    # Vérifier que la zone existe
    zone = crud_zone.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} non trouvée"
        )
    
    # Vérifier que la source existe
    source = crud_source.get_source(db, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} non trouvée"
        )
    
    try:
        # Récupérer et transformer les données
        openmeteo = OpenMeteoService()
        indicators = await openmeteo.fetch_and_transform_weather(
            zone_id=zone_id,
            source_id=source_id,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        
        if not indicators:
            return MessageResponse(
                message="Aucune donnée météo disponible"
            )
        
        # Insérer en bulk
        created = crud_indicator.create_indicators_bulk(db, indicators, current_user.id)
        
        return MessageResponse(
            message=f"{len(created)} indicateurs météo Open-Meteo insérés avec succès"
        )
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la récupération des données Open-Meteo: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue: {str(e)}"
        )


@router.post("/openmeteo/air-quality", response_model=MessageResponse)
async def ingest_openmeteo_air_quality(
    zone_id: int = Query(..., gt=0, description="ID de la zone cible"),
    source_id: int = Query(..., gt=0, description="ID de la source Open-Meteo"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    location_name: str = Query("Unknown", description="Nom de la localisation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ingère les données de qualité de l'air depuis Open-Meteo.
    
    Récupère PM10, PM2.5, CO, NO2, SO2, O3, poussières, index UV.
    
    Exemple: POST /ingest/openmeteo/air-quality?zone_id=1&source_id=2&latitude=48.8566&longitude=2.3522&location_name=Paris
    """
    # Vérifier que la zone existe
    zone = crud_zone.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} non trouvée"
        )
    
    # Vérifier que la source existe
    source = crud_source.get_source(db, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} non trouvée"
        )
    
    try:
        # Récupérer et transformer les données
        openmeteo = OpenMeteoService()
        indicators = await openmeteo.fetch_and_transform_air_quality(
            zone_id=zone_id,
            source_id=source_id,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        
        if not indicators:
            return MessageResponse(
                message="Aucune donnée de qualité de l'air disponible"
            )
        
        # Insérer en bulk
        created = crud_indicator.create_indicators_bulk(db, indicators, current_user.id)
        
        return MessageResponse(
            message=f"{len(created)} indicateurs de qualité de l'air Open-Meteo insérés avec succès"
        )
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la récupération des données Open-Meteo: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue: {str(e)}"
        )


@router.post("/openmeteo/full", response_model=MessageResponse)
async def ingest_openmeteo_full(
    zone_id: int = Query(..., gt=0, description="ID de la zone cible"),
    source_id: int = Query(..., gt=0, description="ID de la source Open-Meteo"),
    latitude: float = Query(..., ge=-90, le=90, description="Latitude"),
    longitude: float = Query(..., ge=-180, le=180, description="Longitude"),
    location_name: str = Query("Unknown", description="Nom de la localisation"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Ingère toutes les données Open-Meteo (météo + qualité de l'air) en une seule requête.
    
    Exemple: POST /ingest/openmeteo/full?zone_id=1&source_id=2&latitude=48.8566&longitude=2.3522&location_name=Paris
    """
    # Vérifier que la zone existe
    zone = crud_zone.get_zone(db, zone_id)
    if not zone:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} non trouvée"
        )
    
    # Vérifier que la source existe
    source = crud_source.get_source(db, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Source {source_id} non trouvée"
        )
    
    try:
        openmeteo = OpenMeteoService()
        
        # Récupérer les deux types de données en parallèle
        weather_indicators = await openmeteo.fetch_and_transform_weather(
            zone_id=zone_id,
            source_id=source_id,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        
        air_quality_indicators = await openmeteo.fetch_and_transform_air_quality(
            zone_id=zone_id,
            source_id=source_id,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name
        )
        
        # Combiner toutes les données
        all_indicators = weather_indicators + air_quality_indicators
        
        if not all_indicators:
            return MessageResponse(
                message="Aucune donnée disponible"
            )
        
        # Insérer en bulk
        created = crud_indicator.create_indicators_bulk(db, all_indicators, current_user.id)
        
        return MessageResponse(
            message=f"{len(created)} indicateurs Open-Meteo insérés avec succès ({len(weather_indicators)} météo, {len(air_quality_indicators)} qualité de l'air)"
        )
        
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Erreur lors de la récupération des données Open-Meteo: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue: {str(e)}"
        )
