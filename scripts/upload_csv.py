#!/usr/bin/env python3
"""
Script CLI pour uploader et parser des fichiers CSV locaux.
Usage: 
    python scripts/upload_csv.py --file data/FR_E2_2025-01-01.csv --zone-id 1 --source-id 1 --type air_quality --limit 100
    python scripts/upload_csv.py --file data/conso-elec-gaz.csv --zone-id 1 --source-id 2 --type energy_consumption
"""
import sys
import os
import argparse

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.services.csv_parser import CSVParserService
from app.crud import indicator as crud_indicator
from app.crud import zone as crud_zone
from app.crud import source as crud_source


def upload_csv(args):
    """Upload et parse un fichier CSV."""
    db = SessionLocal()
    
    try:
        # Vérifier que le fichier existe
        if not os.path.exists(args.file):
            print(f"❌ Fichier non trouvé: {args.file}")
            return
        
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
        
        print(f"📁 Lecture du fichier: {args.file}")
        print(f"   Zone: {zone.name} (ID: {args.zone_id})")
        print(f"   Source: {source.name} (ID: {args.source_id})")
        
        # Lire le fichier
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                file_content = f.read()
        except UnicodeDecodeError:
            # Essayer avec latin-1 pour les fichiers français
            with open(args.file, 'r', encoding='latin-1') as f:
                file_content = f.read()
        
        print(f"🔄 Parsing du fichier...")
        
        # Parser le CSV
        if args.type:
            # Type spécifié manuellement
            indicators = CSVParserService.parse(
                file_content, 
                args.type, 
                args.zone_id, 
                args.source_id,
                args.limit
            )
        else:
            # Détection automatique
            indicators = CSVParserService.parse_auto(
                file_content, 
                args.zone_id, 
                args.source_id,
                args.limit
            )
        
        if not indicators:
            print("⚠️  Aucun indicateur valide trouvé")
            return
        
        print(f"📊 {len(indicators)} indicateurs parsés")
        
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
        import traceback
        traceback.print_exc()
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Script d'upload de fichiers CSV")
    parser.add_argument('--file', required=True, help='Chemin vers le fichier CSV')
    parser.add_argument('--zone-id', type=int, required=True, help='ID de la zone')
    parser.add_argument('--source-id', type=int, required=True, help='ID de la source')
    parser.add_argument('--type', choices=['air_quality', 'energy_consumption'], 
                       help='Type de dataset (auto-détecté si absent)')
    parser.add_argument('--limit', type=int, help='Nombre max de lignes à parser')
    
    args = parser.parse_args()
    
    print("🌍 EcoTrack - Upload CSV\n")
    upload_csv(args)


if __name__ == "__main__":
    main()
