"""
Service de parsing CSV pour les datasets data.gouv.fr
"""
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import io

from app.schemas.indicator import IndicatorCreate


class AirQualityParser:
    """Parser pour les données de qualité de l'air (format data.gouv.fr)."""
    
    POLLUTANT_MAPPING = {
        'NO': 'air_quality_no',
        'NO2': 'air_quality_no2',
        'PM10': 'air_quality_pm10',
        'PM2.5': 'air_quality_pm25',
        'O3': 'air_quality_o3',
        'SO2': 'air_quality_so2',
        'CO': 'air_quality_co'
    }
    
    @staticmethod
    def parse_csv(
        file_content: str,
        zone_id: int,
        source_id: int,
        limit: Optional[int] = None
    ) -> List[IndicatorCreate]:
        """
        Parse un fichier CSV de qualité de l'air.
        
        Args:
            file_content: Contenu du fichier CSV
            zone_id: ID de la zone EcoTrack
            source_id: ID de la source EcoTrack
            limit: Nombre max de lignes à parser
            
        Returns:
            Liste d'indicateurs
        """
        indicators = []
        reader = csv.DictReader(io.StringIO(file_content), delimiter=';')
        
        for idx, row in enumerate(reader):
            if limit and idx >= limit:
                break
            
            try:
                # Extraction des données
                date_debut = row.get('Date de début', '')
                polluant = row.get('Polluant', '')
                valeur = row.get('valeur', '')
                unite = row.get('unité de mesure', '')
                site = row.get('nom site', 'Unknown')
                ville = row.get('Zas', 'Unknown')
                
                # Validation
                if not valeur or not polluant:
                    continue
                
                # Conversion de la date
                try:
                    timestamp = datetime.strptime(date_debut, '%Y/%m/%d %H:%M:%S')
                except:
                    timestamp = datetime.utcnow()
                
                # Type d'indicateur
                indicator_type = AirQualityParser.POLLUTANT_MAPPING.get(
                    polluant, 
                    'air_quality'
                )
                
                # Métadonnées
                meta_info = {
                    'site': site,
                    'ville': ville,
                    'polluant': polluant,
                    'type_implantation': row.get('type d\'implantation', ''),
                    'organisme': row.get('Organisme', '')
                }
                
                indicator = IndicatorCreate(
                    type=indicator_type,
                    name=f"{polluant} - {site}",
                    value=float(valeur.replace(',', '.')),
                    unit=unite,
                    timestamp=timestamp,
                    meta_info=str(meta_info),
                    zone_id=zone_id,
                    source_id=source_id
                )
                indicators.append(indicator)
                
            except Exception as e:
                # Skip ligne invalide
                print(f"⚠️  Ligne ignorée: {e}")
                continue
        
        return indicators


class EnergyConsumptionParser:
    """Parser pour les données de consommation énergétique (format data.gouv.fr)."""
    
    SECTORS = {
        'Agriculture': 'energy_agriculture',
        'Industrie': 'energy_industrie',
        'Tertiaire': 'energy_tertiaire',
        'Résidentiel': 'energy_residentiel'
    }
    
    @staticmethod
    def parse_csv(
        file_content: str,
        zone_id: int,
        source_id: int,
        limit: Optional[int] = None
    ) -> List[IndicatorCreate]:
        """
        Parse un fichier CSV de consommation énergétique.
        
        Args:
            file_content: Contenu du fichier CSV
            zone_id: ID de la zone EcoTrack
            source_id: ID de la source EcoTrack
            limit: Nombre max de lignes à parser
            
        Returns:
            Liste d'indicateurs
        """
        indicators = []
        reader = csv.DictReader(io.StringIO(file_content), delimiter=';')
        
        for idx, row in enumerate(reader):
            if limit and idx >= limit:
                break
            
            try:
                # Extraction des données communes
                commune = row.get('Libellé Commune', 'Unknown')
                code_commune = row.get('Code Commune', '')
                annee = row.get('Année', '')
                filiere = row.get('Filière', 'Unknown')  # Électricité ou Gaz
                
                # Date fictive (1er janvier de l'année)
                try:
                    timestamp = datetime(int(annee), 1, 1)
                except:
                    timestamp = datetime.utcnow()
                
                # Créer un indicateur par secteur
                for sector_col, sector_type in EnergyConsumptionParser.SECTORS.items():
                    conso_key = f'Consommation {sector_col} (MWh)'
                    conso_value = row.get(conso_key, '0.0')
                    
                    # Skip si pas de consommation
                    try:
                        conso = float(conso_value.replace(',', '.'))
                        if conso <= 0:
                            continue
                    except:
                        continue
                    
                    # Métadonnées
                    meta_info = {
                        'commune': commune,
                        'code_commune': code_commune,
                        'filiere': filiere,
                        'secteur': sector_col,
                        'operateur': row.get('Opérateur', ''),
                        'code_postal': row.get('Code_postal', ''),
                        'departement': row.get('Libellé Département', ''),
                        'region': row.get('Libellé Région', '')
                    }
                    
                    indicator = IndicatorCreate(
                        type=sector_type,
                        name=f"{filiere} {sector_col} - {commune}",
                        value=conso,
                        unit='MWh',
                        timestamp=timestamp,
                        meta_info=str(meta_info),
                        zone_id=zone_id,
                        source_id=source_id
                    )
                    indicators.append(indicator)
                
            except Exception as e:
                # Skip ligne invalide
                print(f"⚠️  Ligne ignorée: {e}")
                continue
        
        return indicators


class CSVParserService:
    """Service principal de parsing CSV."""
    
    PARSERS = {
        'air_quality': AirQualityParser,
        'energy_consumption': EnergyConsumptionParser
    }
    
    @staticmethod
    def detect_format(file_content: str) -> Optional[str]:
        """
        Détecte automatiquement le format du CSV.
        
        Args:
            file_content: Contenu du fichier CSV
            
        Returns:
            Type de dataset détecté ou None
        """
        lines = file_content.split('\n')
        if not lines:
            return None
        
        header = lines[0].lower()
        
        # Détection qualité de l'air
        if 'polluant' in header and 'valeur' in header:
            return 'air_quality'
        
        # Détection consommation énergétique
        if 'consommation' in header and 'mwh' in header:
            return 'energy_consumption'
        
        return None
    
    @staticmethod
    def parse(
        file_content: str,
        dataset_type: str,
        zone_id: int,
        source_id: int,
        limit: Optional[int] = None
    ) -> List[IndicatorCreate]:
        """
        Parse un fichier CSV selon son type.
        
        Args:
            file_content: Contenu du fichier CSV
            dataset_type: Type de dataset (air_quality, energy_consumption)
            zone_id: ID de la zone
            source_id: ID de la source
            limit: Limite de lignes à parser
            
        Returns:
            Liste d'indicateurs
        """
        parser_class = CSVParserService.PARSERS.get(dataset_type)
        if not parser_class:
            raise ValueError(f"Type de dataset non supporté: {dataset_type}")
        
        return parser_class.parse_csv(file_content, zone_id, source_id, limit)
    
    @staticmethod
    def parse_auto(
        file_content: str,
        zone_id: int,
        source_id: int,
        limit: Optional[int] = None
    ) -> List[IndicatorCreate]:
        """
        Parse un fichier CSV avec détection automatique du format.
        
        Args:
            file_content: Contenu du fichier CSV
            zone_id: ID de la zone
            source_id: ID de la source
            limit: Limite de lignes à parser
            
        Returns:
            Liste d'indicateurs
        """
        dataset_type = CSVParserService.detect_format(file_content)
        if not dataset_type:
            raise ValueError("Format de fichier non reconnu")
        
        print(f"📋 Format détecté: {dataset_type}")
        return CSVParserService.parse(file_content, dataset_type, zone_id, source_id, limit)
