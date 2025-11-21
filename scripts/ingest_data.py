#!/usr/bin/env python3
"""
Script CLI pour l'ingestion manuelle de données externes.
Usage: 
    python scripts/ingest_data.py openaq --zone-id 1 --source-id 1 --country FR --city Paris
    python scripts/ingest_data.py openmeteo --zone-id 1 --source-id 2 --lat 48.8566 --lon 2.3522 --name Paris
"""
import sys
import os
import asyncio
import argparse

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.services.openaq import OpenAQService
from app.services.openmeteo import OpenMeteoService
from app.crud import indicator as crud_indicator
from app.crud import zone as crud_zone
from app.crud import source as crud_source


async def ingest_openaq(args):
    """Ingère les données OpenAQ."""
    db = SessionLocal()
    
    try:
        # Vérifier que la zone existe
        zone = crud_zone.get_zone(db, args.zone_id)
        if not zone:
            print(f"❌ Zone {args.zone_id} non trouvée")
            return
        
        # Vérifier que la source existe
        source = crud_source.get_source(db, args.source_id)
        if not source:
            print(f"❌ Source {args.source_id} non trouvée")
            return
        
        print(f"🔄 Récupération des données OpenAQ...")
        print(f"   Zone: {zone.name} (ID: {args.zone_id})")
        print(f"   Source: {source.name} (ID: {args.source_id})")
        print(f"   Pays: {args.country}")
        if args.city:
            print(f"   Ville: {args.city}")
        
        # Récupérer et transformer les données
        openaq = OpenAQService(api_key=args.api_key)
        indicators = await openaq.fetch_and_transform(
            zone_id=args.zone_id,
            source_id=args.source_id,
            country=args.country,
            city=args.city,
            limit=args.limit
        )
        
        if not indicators:
            print("⚠️  Aucune donnée disponible")
            return
        
        print(f"📊 {len(indicators)} indicateurs récupérés")
        
        # Insérer en bulk (avec owner_id = 1 pour le script)
        created = crud_indicator.create_indicators_bulk(db, indicators, owner_id=1)
        
        print(f"✅ {len(created)} indicateurs insérés avec succès!")
        
        # Afficher un échantillon
        if created:
            print("\n📋 Échantillon des données insérées:")
            for ind in created[:5]:
                print(f"   - {ind.name}: {ind.value} {ind.unit} @ {ind.timestamp}")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    finally:
        db.close()


async def ingest_openmeteo(args):
    """Ingère les données Open-Meteo."""
    db = SessionLocal()
    
    try:
        # Vérifier que la zone existe
        zone = crud_zone.get_zone(db, args.zone_id)
        if not zone:
            print(f"❌ Zone {args.zone_id} non trouvée")
            return
        
        # Vérifier que la source existe
        source = crud_source.get_source(db, args.source_id)
        if not source:
            print(f"❌ Source {args.source_id} non trouvée")
            return
        
        print(f"🔄 Récupération des données Open-Meteo...")
        print(f"   Zone: {zone.name} (ID: {args.zone_id})")
        print(f"   Source: {source.name} (ID: {args.source_id})")
        print(f"   Localisation: {args.name} ({args.lat}, {args.lon})")
        
        openmeteo = OpenMeteoService()
        
        all_indicators = []
        
        # Récupérer météo
        if args.type in ['all', 'weather']:
            print("   📡 Récupération données météo...")
            weather_indicators = await openmeteo.fetch_and_transform_weather(
                zone_id=args.zone_id,
                source_id=args.source_id,
                latitude=args.lat,
                longitude=args.lon,
                location_name=args.name
            )
            all_indicators.extend(weather_indicators)
            print(f"      ✓ {len(weather_indicators)} indicateurs météo")
        
        # Récupérer qualité de l'air
        if args.type in ['all', 'air_quality']:
            print("   📡 Récupération données qualité de l'air...")
            air_quality_indicators = await openmeteo.fetch_and_transform_air_quality(
                zone_id=args.zone_id,
                source_id=args.source_id,
                latitude=args.lat,
                longitude=args.lon,
                location_name=args.name
            )
            all_indicators.extend(air_quality_indicators)
            print(f"      ✓ {len(air_quality_indicators)} indicateurs qualité de l'air")
        
        if not all_indicators:
            print("⚠️  Aucune donnée disponible")
            return
        
        print(f"📊 {len(all_indicators)} indicateurs récupérés au total")
        
        # Insérer en bulk (avec owner_id = 1 pour le script)
        created = crud_indicator.create_indicators_bulk(db, all_indicators, owner_id=1)
        
        print(f"✅ {len(created)} indicateurs insérés avec succès!")
        
        # Afficher un échantillon
        if created:
            print("\n📋 Échantillon des données insérées:")
            for ind in created[:5]:
                print(f"   - {ind.name}: {ind.value} {ind.unit} @ {ind.timestamp}")
        
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Script d'ingestion de données externes")
    subparsers = parser.add_subparsers(dest='command', help='Source de données')
    
    # Commande OpenAQ
    openaq_parser = subparsers.add_parser('openaq', help='Ingérer depuis OpenAQ')
    openaq_parser.add_argument('--zone-id', type=int, required=True, help='ID de la zone')
    openaq_parser.add_argument('--source-id', type=int, required=True, help='ID de la source')
    openaq_parser.add_argument('--country', default='FR', help='Code pays (FR, US, etc.)')
    openaq_parser.add_argument('--city', help='Nom de la ville')
    openaq_parser.add_argument('--limit', type=int, default=100, help='Nombre de mesures')
    openaq_parser.add_argument('--api-key', help='Clé API OpenAQ')
    
    # Commande Open-Meteo
    openmeteo_parser = subparsers.add_parser('openmeteo', help='Ingérer depuis Open-Meteo')
    openmeteo_parser.add_argument('--zone-id', type=int, required=True, help='ID de la zone')
    openmeteo_parser.add_argument('--source-id', type=int, required=True, help='ID de la source')
    openmeteo_parser.add_argument('--lat', type=float, required=True, help='Latitude')
    openmeteo_parser.add_argument('--lon', type=float, required=True, help='Longitude')
    openmeteo_parser.add_argument('--name', default='Unknown', help='Nom de la localisation')
    openmeteo_parser.add_argument('--type', choices=['all', 'weather', 'air_quality'], 
                                   default='all', help='Type de données à récupérer')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🌍 EcoTrack - Ingestion de données externes\n")
    
    if args.command == 'openaq':
        asyncio.run(ingest_openaq(args))
    elif args.command == 'openmeteo':
        asyncio.run(ingest_openmeteo(args))


if __name__ == "__main__":
    main()
