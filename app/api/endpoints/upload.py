"""
Endpoints pour l'upload et le parsing de fichiers CSV.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.db.models.user import User
from app.services.csv_parser import CSVParserService
from app.crud import indicator as crud_indicator
from app.crud import zone as crud_zone
from app.crud import source as crud_source


router = APIRouter()


@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    zone_id: int = None,
    source_id: int = None,
    dataset_type: Optional[str] = None,
    limit: Optional[int] = None,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload et parse un fichier CSV pour créer des indicateurs.
    
    - **file**: Fichier CSV à uploader
    - **zone_id**: ID de la zone (optionnel, créée automatiquement si absent)
    - **source_id**: ID de la source (optionnel, créée automatiquement si absent)
    - **dataset_type**: Type de dataset (air_quality, energy_consumption) - auto-détecté si absent
    - **limit**: Nombre max de lignes à parser (pour tests)
    
    Le parsing se fait en arrière-plan pour les gros fichiers.
    """
    # Vérifier l'extension
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Le fichier doit être au format CSV")
    
    # Lire le contenu du fichier
    try:
        content = await file.read()
        file_content = content.decode('utf-8')
    except UnicodeDecodeError:
        # Essayer avec latin-1 pour les fichiers français
        file_content = content.decode('latin-1')
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erreur de lecture du fichier: {str(e)}")
    
    # Créer zone par défaut si non spécifiée
    if not zone_id:
        from app.schemas.zone import ZoneCreate
        zone = crud_zone.create_zone(
            db, 
            ZoneCreate(
                name=f"Zone - {file.filename}",
                postal_code="00000",
                description="Zone créée automatiquement depuis upload CSV"
            )
        )
        zone_id = zone.id
    else:
        # Vérifier que la zone existe
        zone = crud_zone.get_zone(db, zone_id)
        if not zone:
            raise HTTPException(status_code=404, detail=f"Zone {zone_id} non trouvée")
    
    # Créer source par défaut si non spécifiée
    if not source_id:
        from app.schemas.source import SourceCreate
        source = crud_source.create_source(
            db,
            SourceCreate(
                name=f"Upload - {file.filename}",
                url="",
                format="CSV",
                description="Source créée automatiquement depuis upload CSV"
            )
        )
        source_id = source.id
    else:
        # Vérifier que la source existe
        source = crud_source.get_source(db, source_id)
        if not source:
            raise HTTPException(status_code=404, detail=f"Source {source_id} non trouvée")
    
    # Parser le CSV
    try:
        if dataset_type:
            # Type spécifié manuellement
            indicators = CSVParserService.parse(
                file_content, 
                dataset_type, 
                zone_id, 
                source_id,
                limit
            )
        else:
            # Détection automatique
            indicators = CSVParserService.parse_auto(
                file_content, 
                zone_id, 
                source_id,
                limit
            )
        
        if not indicators:
            raise HTTPException(status_code=400, detail="Aucun indicateur valide trouvé dans le fichier")
        
        # Insérer les indicateurs
        created = crud_indicator.create_indicators_bulk(
            db, 
            indicators, 
            owner_id=current_user.id
        )
        
        return {
            "message": "Fichier traité avec succès",
            "filename": file.filename,
            "zone_id": zone_id,
            "source_id": source_id,
            "indicators_created": len(created),
            "sample": [
                {
                    "id": ind.id,
                    "type": ind.type,
                    "name": ind.name,
                    "value": ind.value,
                    "unit": ind.unit,
                    "timestamp": ind.timestamp.isoformat()
                }
                for ind in created[:5]
            ]
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")


@router.post("/upload/auto-detect")
async def upload_csv_auto_detect(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload un fichier CSV avec création automatique de zone et source.
    Détecte automatiquement le type de dataset.
    
    Idéal pour un premier test rapide.
    """
    return await upload_csv(
        file=file,
        zone_id=None,
        source_id=None,
        dataset_type=None,
        limit=100,  # Limiter à 100 lignes pour test
        background_tasks=None,
        db=db,
        current_user=current_user
    )


@router.get("/supported-formats")
async def get_supported_formats():
    """
    Retourne la liste des formats CSV supportés.
    """
    return {
        "formats": [
            {
                "type": "air_quality",
                "name": "Qualité de l'air",
                "description": "Données de pollution atmosphérique (data.gouv.fr)",
                "fields": ["Date de début", "Polluant", "valeur", "unité de mesure", "nom site"]
            },
            {
                "type": "energy_consumption",
                "name": "Consommation énergétique",
                "description": "Consommation électricité/gaz par commune (data.gouv.fr)",
                "fields": ["Année", "Filière", "Consommation Agriculture (MWh)", "Code Commune"]
            }
        ]
    }
