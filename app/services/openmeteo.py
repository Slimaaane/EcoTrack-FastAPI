"""
Service d'ingestion de données depuis Open-Meteo (données météorologiques).
API: https://open-meteo.com/
"""
import httpx
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from app.schemas.indicator import IndicatorCreate


class OpenMeteoService:
    """Service pour récupérer les données météo depuis Open-Meteo."""
    
    BASE_URL = "https://api.open-meteo.com/v1"
    
    async def get_current_weather(
        self,
        latitude: float,
        longitude: float,
        timezone: str = "auto"
    ) -> Dict[str, Any]:
        """
        Récupère les données météo actuelles.
        
        Args:
            latitude: Latitude (ex: 48.8566 pour Paris)
            longitude: Longitude (ex: 2.3522 pour Paris)
            timezone: Fuseau horaire (auto, Europe/Paris, etc.)
            
        Returns:
            Données météo brutes
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,wind_direction_10m",
            "timezone": timezone
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/forecast",
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    async def get_air_quality(
        self,
        latitude: float,
        longitude: float,
        timezone: str = "auto"
    ) -> Dict[str, Any]:
        """
        Récupère les données de qualité de l'air.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            timezone: Fuseau horaire
            
        Returns:
            Données de qualité de l'air brutes
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,dust,uv_index",
            "timezone": timezone
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/air-quality",
                    params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            # Si l'endpoint air-quality n'est pas disponible, retourner des données vides
            # plutôt que de faire échouer toute l'opération
            print(f"⚠️  Air quality endpoint non disponible: {e}")
            return {"current": {}}
    
    async def get_historical_weather(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime,
        timezone: str = "auto"
    ) -> Dict[str, Any]:
        """
        Récupère les données météo historiques.
        
        Args:
            latitude: Latitude
            longitude: Longitude
            start_date: Date de début
            end_date: Date de fin
            timezone: Fuseau horaire
            
        Returns:
            Données historiques brutes
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
            "timezone": timezone
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/archive",
                params=params
            )
            response.raise_for_status()
            return response.json()
    
    def transform_current_weather_to_indicators(
        self,
        weather_data: Dict[str, Any],
        zone_id: int,
        source_id: int,
        location_name: str = "Unknown"
    ) -> List[IndicatorCreate]:
        """
        Transforme les données météo actuelles en indicateurs EcoTrack.
        
        Args:
            weather_data: Données brutes Open-Meteo
            zone_id: ID de la zone EcoTrack
            source_id: ID de la source EcoTrack
            location_name: Nom de la localisation
            
        Returns:
            Liste d'indicateurs
        """
        indicators = []
        current = weather_data.get("current", {})
        
        if not current:
            return indicators
        
        timestamp = datetime.utcnow()
        time_str = current.get("time")
        if time_str:
            timestamp = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        
        # Mapping des variables météo vers indicateurs
        weather_mapping = {
            "temperature_2m": ("weather_temperature", "°C", "Température"),
            "relative_humidity_2m": ("weather_humidity", "%", "Humidité relative"),
            "precipitation": ("weather_precipitation", "mm", "Précipitations"),
            "wind_speed_10m": ("weather_wind_speed", "km/h", "Vitesse du vent"),
            "wind_direction_10m": ("weather_wind_direction", "°", "Direction du vent")
        }
        
        for key, (type_name, unit, name_prefix) in weather_mapping.items():
            value = current.get(key)
            if value is not None:
                indicator = IndicatorCreate(
                    type=type_name,
                    name=f"{name_prefix} - {location_name}",
                    value=float(value),
                    unit=unit,
                    timestamp=timestamp,
                    meta_info=str({
                        "location": location_name,
                        "latitude": weather_data.get("latitude"),
                        "longitude": weather_data.get("longitude")
                    }),
                    zone_id=zone_id,
                    source_id=source_id
                )
                indicators.append(indicator)
        
        return indicators
    
    def transform_air_quality_to_indicators(
        self,
        air_quality_data: Dict[str, Any],
        zone_id: int,
        source_id: int,
        location_name: str = "Unknown"
    ) -> List[IndicatorCreate]:
        """
        Transforme les données de qualité de l'air en indicateurs EcoTrack.
        
        Args:
            air_quality_data: Données brutes Open-Meteo
            zone_id: ID de la zone EcoTrack
            source_id: ID de la source EcoTrack
            location_name: Nom de la localisation
            
        Returns:
            Liste d'indicateurs
        """
        indicators = []
        current = air_quality_data.get("current", {})
        
        if not current:
            return indicators
        
        timestamp = datetime.utcnow()
        time_str = current.get("time")
        if time_str:
            timestamp = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        
        # Mapping des polluants vers indicateurs
        air_quality_mapping = {
            "pm10": ("air_quality", "µg/m³", "PM10"),
            "pm2_5": ("air_quality", "µg/m³", "PM2.5"),
            "carbon_monoxide": ("air_quality", "µg/m³", "CO (Monoxyde de carbone)"),
            "nitrogen_dioxide": ("air_quality", "µg/m³", "NO2 (Dioxyde d'azote)"),
            "sulphur_dioxide": ("air_quality", "µg/m³", "SO2 (Dioxyde de soufre)"),
            "ozone": ("air_quality", "µg/m³", "O3 (Ozone)"),
            "dust": ("air_quality", "µg/m³", "Poussières"),
            "uv_index": ("weather_uv", "index", "Index UV")
        }
        
        for key, (type_name, unit, name_prefix) in air_quality_mapping.items():
            value = current.get(key)
            if value is not None:
                indicator = IndicatorCreate(
                    type=type_name,
                    name=f"{name_prefix} - {location_name}",
                    value=float(value),
                    unit=unit,
                    timestamp=timestamp,
                    meta_info=str({
                        "location": location_name,
                        "latitude": air_quality_data.get("latitude"),
                        "longitude": air_quality_data.get("longitude")
                    }),
                    zone_id=zone_id,
                    source_id=source_id
                )
                indicators.append(indicator)
        
        return indicators
    
    async def fetch_and_transform_weather(
        self,
        zone_id: int,
        source_id: int,
        latitude: float,
        longitude: float,
        location_name: str = "Unknown"
    ) -> List[IndicatorCreate]:
        """
        Récupère et transforme les données météo en une seule opération.
        
        Args:
            zone_id: ID de la zone EcoTrack
            source_id: ID de la source EcoTrack
            latitude: Latitude
            longitude: Longitude
            location_name: Nom de la localisation
            
        Returns:
            Liste d'indicateurs prêts à être insérés
        """
        weather_data = await self.get_current_weather(latitude, longitude)
        return self.transform_current_weather_to_indicators(
            weather_data, zone_id, source_id, location_name
        )
    
    async def fetch_and_transform_air_quality(
        self,
        zone_id: int,
        source_id: int,
        latitude: float,
        longitude: float,
        location_name: str = "Unknown"
    ) -> List[IndicatorCreate]:
        """
        Récupère et transforme les données de qualité de l'air en une seule opération.
        
        Args:
            zone_id: ID de la zone EcoTrack
            source_id: ID de la source EcoTrack
            latitude: Latitude
            longitude: Longitude
            location_name: Nom de la localisation
            
        Returns:
            Liste d'indicateurs prêts à être insérés
        """
        try:
            air_quality_data = await self.get_air_quality(latitude, longitude)
            return self.transform_air_quality_to_indicators(
                air_quality_data, zone_id, source_id, location_name
            )
        except Exception as e:
            print(f"⚠️  Impossible de récupérer les données de qualité de l'air: {e}")
            return []
