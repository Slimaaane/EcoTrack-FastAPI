"""
Service d'ingestion de données depuis OpenAQ (qualité de l'air).
API: https://docs.openaq.org/
"""
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from app.schemas.indicator import IndicatorCreate


class OpenAQService:
    """Service pour récupérer les données de qualité de l'air depuis OpenAQ."""
    
    BASE_URL = "https://api.openaq.org/v3"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialise le service OpenAQ.
        
        Args:
            api_key: Clé API OpenAQ (optionnelle mais recommandée)
        """
        self.api_key = api_key
        self.headers = {}
        if api_key:
            self.headers["X-API-Key"] = api_key
    
    async def get_latest_measurements(
        self,
        country: str = "FR",
        city: Optional[str] = None,
        parameter: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les dernières mesures de qualité de l'air.
        
        Args:
            country: Code pays ISO (ex: FR, US, GB)
            city: Nom de la ville (optionnel)
            parameter: Paramètre à mesurer (pm25, pm10, o3, no2, so2, co)
            limit: Nombre de résultats max
            
        Returns:
            Liste de mesures brutes
        """
        params = {
            "countries": country,
            "limit": limit,
            "order_by": "datetime",
            "sort": "desc"
        }
        
        if parameter:
            params["parameters_id"] = parameter
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # OpenAQ v3 utilise l'endpoint /locations/latest
                response = await client.get(
                    f"{self.BASE_URL}/locations/latest",
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
        except httpx.HTTPStatusError as e:
            print(f"⚠️  OpenAQ API non disponible: {e}")
            return []
    
    async def get_measurements_by_location(
        self,
        location_id: int,
        parameter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Récupère les mesures pour une station spécifique.
        
        Args:
            location_id: ID de la station OpenAQ
            parameter: Paramètre à mesurer
            date_from: Date de début
            date_to: Date de fin
            limit: Nombre de résultats max
            
        Returns:
            Liste de mesures brutes
        """
        params = {
            "location_id": location_id,
            "limit": limit,
            "order_by": "datetime",
            "sort": "desc"
        }
        
        if parameter:
            params["parameter"] = parameter
        
        if date_from:
            params["date_from"] = date_from.isoformat()
        
        if date_to:
            params["date_to"] = date_to.isoformat()
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/measurements",
                params=params,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
    
    def transform_to_indicators(
        self,
        measurements: List[Dict[str, Any]],
        zone_id: int,
        source_id: int
    ) -> List[IndicatorCreate]:
        """
        Transforme les données OpenAQ v3 en indicateurs EcoTrack.
        
        Args:
            measurements: Liste de mesures brutes OpenAQ
            zone_id: ID de la zone EcoTrack
            source_id: ID de la source EcoTrack
            
        Returns:
            Liste d'indicateurs prêts à être créés
        """
        indicators = []
        
        for location in measurements:
            location_name = location.get("name", "Unknown")
            coordinates = location.get("coordinates", {})
            
            # Parcourir tous les paramètres de cette localisation
            latest = location.get("latest", {})
            
            for param_id, param_data in latest.items():
                if not isinstance(param_data, dict):
                    continue
                
                value = param_data.get("value")
                unit = param_data.get("unit", "")
                
                # Date de la mesure
                date_str = param_data.get("datetime")
                if date_str:
                    try:
                        timestamp = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    except:
                        timestamp = datetime.utcnow()
                else:
                    timestamp = datetime.utcnow()
                
                # Métadonnées supplémentaires
                meta_info = {
                    "location": location_name,
                    "coordinates": coordinates,
                    "parameter_id": param_id,
                    "country": location.get("country", {}).get("name")
                }
                
                if value is not None:
                    indicator = IndicatorCreate(
                        type="air_quality",
                        name=f"{param_id.upper()} - {location_name}",
                        value=float(value),
                        unit=unit,
                        timestamp=timestamp,
                        meta_info=str(meta_info),
                        zone_id=zone_id,
                        source_id=source_id
                    )
                    indicators.append(indicator)
        
        return indicators
    
    async def fetch_and_transform(
        self,
        zone_id: int,
        source_id: int,
        country: str = "FR",
        city: Optional[str] = None,
        limit: int = 100
    ) -> List[IndicatorCreate]:
        """
        Récupère et transforme les données en une seule opération.
        
        Args:
            zone_id: ID de la zone EcoTrack
            source_id: ID de la source EcoTrack
            country: Code pays
            city: Nom de la ville
            limit: Nombre de résultats max
            
        Returns:
            Liste d'indicateurs prêts à être insérés
        """
        measurements = await self.get_latest_measurements(
            country=country,
            city=city,
            limit=limit
        )
        
        return self.transform_to_indicators(measurements, zone_id, source_id)
