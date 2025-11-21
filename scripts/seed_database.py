#!/usr/bin/env python3
"""
Script pour initialiser la base de données avec des données de démonstration.
Usage: python scripts/seed_database.py
"""
import sys
import os
from datetime import datetime, timedelta
import random

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.db.models.user import User, UserRole
from app.db.models.zone import Zone
from app.db.models.source import Source
from app.db.models.indicator import Indicator
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError


def create_users(db):
    """Crée des utilisateurs de test."""
    print("👥 Création des utilisateurs...")
    
    users_data = [
        {
            "email": "admin@ecotrack.com",
            "username": "admin",
            "password": "admin123",
            "role": UserRole.ADMIN
        },
        {
            "email": "user@ecotrack.com",
            "username": "user",
            "password": "user123",
            "role": UserRole.USER
        },
        {
            "email": "analyst@ecotrack.com",
            "username": "analyst",
            "password": "analyst123",
            "role": UserRole.USER
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            print(f"   ⚠️  Utilisateur {user_data['username']} existe déjà")
            created_users.append(existing)
            continue
        
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=get_password_hash(user_data["password"]),
            role=user_data["role"],
            is_active=True
        )
        db.add(user)
        created_users.append(user)
        print(f"   ✓ {user_data['username']} ({user_data['role'].value})")
    
    db.commit()
    return created_users


def create_zones(db):
    """Crée des zones géographiques."""
    print("\n📍 Création des zones...")
    
    zones_data = [
        {
            "name": "Paris Centre",
            "postal_code": "75001",
            "description": "Centre de Paris, Île-de-France"
        },
        {
            "name": "Lyon",
            "postal_code": "69001",
            "description": "Centre de Lyon, Auvergne-Rhône-Alpes"
        },
        {
            "name": "Marseille",
            "postal_code": "13001",
            "description": "Centre de Marseille, Provence-Alpes-Côte d'Azur"
        },
        {
            "name": "Toulouse",
            "postal_code": "31000",
            "description": "Centre de Toulouse, Occitanie"
        },
        {
            "name": "Nice",
            "postal_code": "06000",
            "description": "Centre de Nice, Provence-Alpes-Côte d'Azur"
        }
    ]
    
    created_zones = []
    
    for zone_data in zones_data:
        existing = db.query(Zone).filter(Zone.name == zone_data["name"]).first()
        if existing:
            print(f"   ⚠️  Zone {zone_data['name']} existe déjà")
            created_zones.append(existing)
            continue
        
        zone = Zone(**zone_data)
        db.add(zone)
        created_zones.append(zone)
        print(f"   ✓ {zone_data['name']} ({zone_data['postal_code']})")
    
    db.commit()
    return created_zones


def create_sources(db):
    """Crée des sources de données."""
    print("\n📊 Création des sources...")
    
    sources_data = [
        {
            "name": "OpenAQ",
            "url": "https://openaq.org",
            "format": "JSON",
            "frequency": "real-time",
            "limitations": "Rate limit: 10000 requêtes/jour avec clé API",
            "description": "Données de qualité de l'air en temps réel"
        },
        {
            "name": "Open-Meteo",
            "url": "https://open-meteo.com",
            "format": "JSON",
            "frequency": "hourly",
            "limitations": "Usage gratuit sans limite pour usage non-commercial",
            "description": "Données météorologiques et qualité de l'air"
        },
        {
            "name": "Manual Entry",
            "url": None,
            "format": "CSV",
            "frequency": "on-demand",
            "limitations": None,
            "description": "Saisie manuelle ou import CSV"
        },
        {
            "name": "Government Sensors",
            "url": "https://www.data.gouv.fr",
            "format": "CSV",
            "frequency": "daily",
            "limitations": None,
            "description": "Capteurs gouvernementaux français"
        }
    ]
    
    created_sources = []
    
    for source_data in sources_data:
        existing = db.query(Source).filter(Source.name == source_data["name"]).first()
        if existing:
            print(f"   ⚠️  Source {source_data['name']} existe déjà")
            created_sources.append(existing)
            continue
        
        source = Source(**source_data)
        db.add(source)
        created_sources.append(source)
        print(f"   ✓ {source_data['name']}")
    
    db.commit()
    return created_sources


def create_sample_indicators(db, users, zones, sources):
    """Crée des indicateurs de démonstration."""
    print("\n📈 Création d'indicateurs de démonstration...")
    
    # Types d'indicateurs avec leurs unités
    indicator_types = [
        ("air_quality", [
            ("PM2.5", "µg/m³", 10, 50),
            ("PM10", "µg/m³", 15, 80),
            ("NO2", "µg/m³", 20, 100),
            ("O3", "µg/m³", 30, 120)
        ]),
        ("weather_temperature", [
            ("Température", "°C", 5, 30)
        ]),
        ("weather_humidity", [
            ("Humidité", "%", 40, 80)
        ]),
        ("energy", [
            ("Consommation électrique", "kWh", 100, 500)
        ]),
        ("waste", [
            ("Déchets collectés", "kg", 50, 200)
        ])
    ]
    
    count = 0
    
    # Créer 30 jours de données pour chaque zone
    for zone in zones[:3]:  # Limiter aux 3 premières zones
        for days_ago in range(30):
            timestamp = datetime.utcnow() - timedelta(days=days_ago)
            
            for type_name, measurements in indicator_types:
                for name, unit, min_val, max_val in measurements:
                    # Variation aléatoire mais réaliste
                    value = random.uniform(min_val, max_val)
                    
                    indicator = Indicator(
                        type=type_name,
                        name=f"{name} - {zone.name}",
                        value=value,
                        unit=unit,
                        timestamp=timestamp,
                        meta_info=str({"simulated": True, "day": days_ago}),
                        zone_id=zone.id,
                        source_id=sources[2].id,  # Manual Entry
                        owner_id=users[0].id  # Admin
                    )
                    db.add(indicator)
                    count += 1
    
    db.commit()
    print(f"   ✓ {count} indicateurs créés")
    return count


def main():
    """Point d'entrée principal."""
    print("🌍 EcoTrack - Initialisation de la base de données\n")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Créer les utilisateurs
        users = create_users(db)
        
        # Créer les zones
        zones = create_zones(db)
        
        # Créer les sources
        sources = create_sources(db)
        
        # Créer des indicateurs de démonstration
        indicator_count = create_sample_indicators(db, users, zones, sources)
        
        print("\n" + "=" * 60)
        print("✅ Base de données initialisée avec succès!")
        print(f"\n📊 Résumé:")
        print(f"   - {len(users)} utilisateurs")
        print(f"   - {len(zones)} zones")
        print(f"   - {len(sources)} sources")
        print(f"   - {indicator_count} indicateurs")
        
        print(f"\n🔐 Comptes créés:")
        print(f"   Admin:   admin@ecotrack.com / admin123")
        print(f"   User:    user@ecotrack.com / user123")
        print(f"   Analyst: analyst@ecotrack.com / analyst123")
        
        print(f"\n💡 Prochaines étapes:")
        print(f"   1. Démarrer le serveur: uvicorn app.main:app --reload")
        print(f"   2. Tester l'API: http://127.0.0.1:8000/docs")
        print(f"   3. Ingérer des données réelles:")
        print(f"      python scripts/ingest_data.py openaq --zone-id 1 --source-id 1 --country FR --city Paris")
        print(f"      python scripts/ingest_data.py openmeteo --zone-id 1 --source-id 2 --lat 48.8566 --lon 2.3522 --name Paris")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
