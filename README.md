# 🌍 EcoTrack FastAPI

**API REST complète pour la collecte, le stockage et la visualisation d'indicateurs environnementaux**

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-37%20passed-success.svg)](tests/)
[![Coverage](https://img.shields.io/badge/Coverage-58%25-yellow.svg)](htmlcov/)

> **Projet académique** - EFREI Paris - 20 novembre 2025  
> Mise en application des concepts avancés de développement d'API avec FastAPI

## 📋 Table des matières

- [Contexte académique](#contexte-académique)
- [Objectifs pédagogiques](#objectifs-pédagogiques)
- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [API Documentation](#api-documentation)
- [Sources de données](#sources-de-données)
- [Tests](#tests)
- [Méthodologie](#méthodologie)
- [Livrables](#livrables)

---

## 🎓 Contexte académique

### Thématique choisie
**Suivi d'indicateurs environnementaux locaux** : qualité de l'air, consommation énergétique par secteur d'activité.

Le service vise à agréger des séries temporelles d'indicateurs par zone géographique (ville/code postal) et à fournir des endpoints pour analyses et visualisations.

### Problématique
Comment centraliser et rendre accessible des données environnementales hétérogènes issues de sources ouvertes françaises, tout en offrant une API sécurisée, performante et facilement consommable par des applications tierces ?

---

## 🎯 Objectifs pédagogiques

Ce projet met en application l'ensemble des notions vues en cours :

✅ **Architecture API REST** : Conception et implémentation d'une API maintenable avec FastAPI  
✅ **Validation de données** : Utilisation de Pydantic pour la validation stricte des schémas  
✅ **Authentification JWT** : Implémentation complète avec gestion de tokens sécurisés  
✅ **Role-Based Access Control (RBAC)** : Système de permissions admin/user  
✅ **ORM et migrations** : SQLAlchemy 2.0 avec Alembic pour la gestion de la base de données  
✅ **Ingestion de données externes** : Scripts d'import CSV depuis data.gouv.fr  
✅ **Tests et qualité** : Suite de tests pytest avec 58% de couverture  
✅ **Filtres et pagination** : Endpoints de recherche avancée avec agrégations  
✅ **Statistiques** : Calculs d'agrégations (min, max, moyenne, tendances)  
✅ **Documentation** : Swagger UI automatique et README complet  
✅ **Frontend** : Dashboard web interactif avec Chart.js  

---

## 🎯 Vue d'ensemble

EcoTrack est une plateforme de suivi d'indicateurs environnementaux qui permet de :
- **Collecter** des données environnementales depuis des sources ouvertes (data.gouv.fr)
- **Stocker** les indicateurs dans une base de données SQLite
- **Analyser** les tendances avec des statistiques avancées
- **Visualiser** les données via un dashboard web interactif

### Technologies utilisées

- **Backend** : FastAPI 0.104+, SQLAlchemy 2.0+, Python 3.13
- **Authentification** : JWT avec python-jose, bcrypt
- **Base de données** : SQLite avec Alembic pour les migrations
- **Frontend** : HTML/CSS/JavaScript vanilla + Chart.js
- **Tests** : pytest avec couverture de 58%
- **Validation** : Pydantic 2.5+

---

## ✨ Fonctionnalités

### 🔐 Authentification & Autorisation
- Inscription et connexion avec JWT
- Système de rôles (admin/user)
- Protection RBAC sur tous les endpoints

### 📊 Gestion des indicateurs
- **Types supportés** :
  - Qualité de l'air (NO, NO2, O3, PM10, PM2.5, SO2, CO)
  - Consommation d'énergie (Agriculture, Industrie, Tertiaire, Résidentiel)
  - Extensible à d'autres types

- **Opérations** :
  - CRUD complet
  - Filtres avancés (type, zone, source, dates)
  - Pagination et tri
  - Création en masse

### 🗺️ Zones géographiques
- Gestion des zones avec codes postaux
- Support GeoJSON (préparé pour extension)

### 🔗 Sources de données
- Configuration des sources externes
- Support CSV, JSON, API
- Métadonnées (fréquence, format, limitations)

### 📈 Statistiques
- Distribution par type d'indicateur
- Résumés statistiques (min, max, moyenne, count)
- Tendances temporelles
- Comparaisons géographiques

### 📤 Import CSV
- Détection automatique du format
- Parsers pour données data.gouv.fr :
  - FR_E2 (qualité de l'air)
  - Consommation électricité/gaz par commune
- Upload via API ou script CLI

### 🖥️ Dashboard Web
- Interface de connexion/inscription
- Filtres interactifs (type, zone, source, limite)
- Tableau paginé des indicateurs
- Graphiques Chart.js des tendances
- Cartes statistiques en temps réel

---

## 🏗️ Architecture

```
EcoTrack-FastAPI/
├── app/
│   ├── api/
│   │   ├── endpoints/      # Routes API
│   │   │   ├── auth.py     # Authentification
│   │   │   ├── users.py    # Gestion utilisateurs
│   │   │   ├── zones.py    # Zones géographiques
│   │   │   ├── sources.py  # Sources de données
│   │   │   ├── indicators.py  # Indicateurs
│   │   │   ├── stats.py    # Statistiques
│   │   │   └── upload.py   # Upload CSV
│   │   ├── deps.py         # Dépendances (auth, DB)
│   │   └── main.py         # Configuration routes
│   ├── core/
│   │   ├── config.py       # Configuration app
│   │   └── security.py     # JWT, hash passwords
│   ├── crud/               # Opérations base de données
│   ├── db/
│   │   ├── models/         # Modèles SQLAlchemy
│   │   ├── base.py         # Base déclarative
│   │   └── session.py      # Session DB
│   ├── schemas/            # Schémas Pydantic
│   ├── services/           # Services métier
│   │   ├── csv_parser.py   # Parsers CSV
│   │   ├── openaq.py       # API OpenAQ (legacy)
│   │   └── openmeteo.py    # API Open-Meteo (legacy)
│   └── main.py             # Point d'entrée FastAPI
├── frontend/               # Dashboard web
│   ├── index.html          # Interface utilisateur
│   └── dashboard.js        # Logique frontend
├── tests/                  # Suite de tests pytest
├── scripts/                # Scripts utilitaires
├── data/                   # Données CSV
├── alembic/                # Migrations DB
└── ecotrack.db             # Base SQLite
```

### Modèle de données

```
User (utilisateur)
  ├── id, email, username, hashed_password
  ├── role (admin/user)
  └── is_active

Zone (zone géographique)
  ├── id, name, postal_code
  ├── geom (GeoJSON)
  └── description

Source (source de données)
  ├── id, name, url
  ├── format, frequency
  └── limitations, description

Indicator (indicateur)
  ├── id, type, name
  ├── value, unit, timestamp
  ├── zone_id → Zone
  ├── source_id → Source
  ├── owner_id → User
  └── meta_info (JSON)
```

---

## 🚀 Installation

### Prérequis
- Python 3.13+
- pip

### 1. Cloner le projet
```bash
git clone https://github.com/Slimaaane/EcoTrack-FastAPI.git
cd EcoTrack-FastAPI
```

### 2. Créer l'environnement virtuel
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Installer les dépendances
```powershell
pip install -r requirements.txt
```

### 4. Initialiser la base de données
```powershell
# Créer les tables
python -c "from app.db.session import engine; from app.db.base import Base; Base.metadata.create_all(bind=engine)"

# Peupler avec des données de test (optionnel)
python scripts/seed.py
```

---

## 💻 Utilisation

### Démarrer le serveur

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Le serveur démarre sur **http://127.0.0.1:8000**

### Accéder au dashboard

Ouvrez votre navigateur : **http://127.0.0.1:8000/dashboard**

**Identifiants par défaut** (après seed.py) :
- Email : `admin@ecotrack.com`
- Mot de passe : `admin123`

### Documentation API interactive

- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

---

## 📡 API Documentation

### Authentification

#### POST `/api/v1/auth/signup`
Créer un nouveau compte utilisateur.

**Body** :
```json
{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "password123",
  "role": "user"
}
```

**Response** (201) :
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "role": "user",
  "is_active": true
}
```

#### POST `/api/v1/auth/login`
Se connecter et obtenir un token JWT.

**Body** (form-data) :
```
username=admin@ecotrack.com
password=admin123
```

**Response** (200) :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Indicateurs

#### GET `/api/v1/indicators`
Liste les indicateurs avec filtres et pagination.

**Query Parameters** :
- `type` : Filtrer par type (ex: `air_quality_no2`)
- `zone_id` : Filtrer par zone
- `source_id` : Filtrer par source
- `from_date` : Date début (ISO 8601)
- `to_date` : Date fin (ISO 8601)
- `skip` : Pagination offset (défaut: 0)
- `limit` : Nombre résultats (défaut: 100, max: 1000)
- `sort_by` : Tri (défaut: `timestamp`)
- `sort_order` : Ordre (`asc` ou `desc`)

**Headers** :
```
Authorization: Bearer <token>
```

**Response** (200) :
```json
{
  "items": [
    {
      "id": 1,
      "type": "air_quality_no2",
      "name": "NO2 Metz Centre",
      "value": 45.5,
      "unit": "µg/m³",
      "timestamp": "2025-01-01T12:00:00",
      "zone_id": 1,
      "source_id": 1,
      "owner_id": 1,
      "meta_info": {}
    }
  ],
  "total": 846,
  "skip": 0,
  "limit": 100,
  "has_more": true
}
```

#### POST `/api/v1/indicators`
Créer un nouvel indicateur.

**Headers** :
```
Authorization: Bearer <token>
```

**Body** :
```json
{
  "type": "air_quality_pm10",
  "name": "PM10 Paris",
  "value": 35.2,
  "unit": "µg/m³",
  "timestamp": "2025-11-21T10:00:00",
  "zone_id": 1,
  "source_id": 1
}
```

**Response** (201) :
```json
{
  "id": 847,
  "type": "air_quality_pm10",
  "name": "PM10 Paris",
  "value": 35.2,
  "unit": "µg/m³",
  "timestamp": "2025-11-21T10:00:00",
  "zone_id": 1,
  "source_id": 1,
  "owner_id": 1,
  "meta_info": {}
}
```

#### DELETE `/api/v1/indicators/{id}`
Supprimer un indicateur (propriétaire ou admin uniquement).

### Statistiques

#### GET `/api/v1/stats/distribution`
Distribution des indicateurs par type.

**Response** (200) :
```json
{
  "zone_id": null,
  "from_date": null,
  "to_date": null,
  "total_types": 11,
  "distribution": [
    {
      "type": "air_quality_no2",
      "count": 50
    },
    {
      "type": "energy_agriculture",
      "count": 2
    }
  ]
}
```

#### GET `/api/v1/stats/summary/{type}`
Résumé statistique pour un type d'indicateur.

**Response** (200) :
```json
{
  "type": "air_quality_no2",
  "zone_id": null,
  "from_date": null,
  "to_date": null,
  "min": 12.3,
  "max": 87.5,
  "avg": 45.2,
  "count": 50
}
```

#### GET `/api/v1/stats/trend/{type}?days=7`
Tendance temporelle d'un indicateur.

### Upload CSV

#### POST `/api/v1/upload/upload`
Uploader et parser un fichier CSV.

**Headers** :
```
Authorization: Bearer <token>
Content-Type: multipart/form-data
```

**Form Data** :
- `file` : Fichier CSV
- `zone_id` : ID de la zone (optionnel)
- `source_id` : ID de la source (optionnel)
- `dataset_type` : Type (`air_quality` ou `energy_consumption`)
- `limit` : Limite de lignes (défaut: 1000)

**Response** (200) :
```json
{
  "message": "50 indicateurs créés avec succès",
  "count": 50,
  "sample": [...]
}
```

### Types d'indicateurs supportés

**Qualité de l'air** :
- `air_quality` (générique)
- `air_quality_no` (Monoxyde d'azote)
- `air_quality_no2` (Dioxyde d'azote)
- `air_quality_o3` (Ozone)
- `air_quality_pm10` (Particules ≤10µm)
- `air_quality_pm25` (Particules ≤2.5µm)
- `air_quality_so2` (Dioxyde de soufre)
- `air_quality_co` (Monoxyde de carbone)

**Énergie** :
- `energy_consumption` (générique)
- `energy_agriculture`
- `energy_industrie`
- `energy_tertiaire`
- `energy_residentiel`

**Météo** (préparé) :
- `weather_temperature`
- `weather_humidity`
- `weather_precipitation`

---

## 🧪 Tests

### Lancer tous les tests
```powershell
python -m pytest tests/ -v
```

### Tests avec couverture
```powershell
python -m pytest tests/ --cov=app --cov-report=html
```

Le rapport HTML est généré dans `htmlcov/index.html`.

### Statistiques des tests
- **37 tests passés** ✅
- **8 tests skipped** (features non implémentées)
- **58% de couverture** du code

**Répartition** :
- Auth : 8 tests (signup, login, JWT, RBAC)
- Zones : 8 tests (CRUD complet + permissions)
- Sources : 7 tests (CRUD + filtres)
- Indicators : 12 tests (CRUD, filtres, pagination, RBAC)
- Statistics : 6 tests (distribution, summary, trends)

### Structure des tests
```
tests/
├── conftest.py           # Fixtures pytest
├── test_auth.py          # Tests authentification
├── test_zones.py         # Tests zones
├── test_sources.py       # Tests sources
├── test_indicators.py    # Tests indicateurs
├── test_stats.py         # Tests statistiques
└── test_csv_parser.py    # Tests parsers CSV
```

---

## 📦 Sources de données

### 🔍 Choix et justification des sources

Le projet intègre **deux sources externes** conformément aux exigences académiques :

#### 1. **Qualité de l'air** - ATMO France (FR_E2)

**URL** : [Données temps réel de mesure des concentrations de polluants atmosphériques](https://www.data.gouv.fr/fr/datasets/donnees-temps-reel-de-mesure-des-concentrations-de-polluants-atmospheriques-reglementes-1/)

**Format** : CSV avec séparateur `;`

**Fréquence** : Temps réel (actualisé toutes les heures)

**Colonnes utilisées** :
- `Date de début` : Timestamp ISO 8601
- `Polluant` : NO, NO2, O3, PM10, PM2.5, SO2, CO
- `valeur` : Concentration mesurée
- `unité` : µg/m³ ou mg/m³
- `nom site` : Nom de la station de mesure

**Limitations** :
- ❌ Pas de coordonnées GPS directes (géolocalisation par nom de ville)
- ❌ Données manquantes pour certaines périodes
- ❌ Variabilité de la qualité selon les stations
- ✅ Pas de quota d'API, fichiers CSV publics

**Justification** : Source officielle des associations agréées de surveillance de la qualité de l'air en France. Données fiables, standardisées au niveau national, couvrant 7 polluants réglementaires.

#### 2. **Consommation énergétique** - data.gouv.fr

**URL** : [Consommation annuelle d'électricité et gaz par commune et par secteur d'activité](https://www.data.gouv.fr/fr/datasets/consommation-annuelle-delectricite-et-gaz-par-commune-et-par-secteur-dactivite/)

**Format** : CSV avec séparateur `;`

**Fréquence** : Annuelle (dernière mise à jour : 2023)

**Colonnes utilisées** :
- `Année` : Année de consommation
- `Code commune INSEE` : Identifiant commune
- `Nom commune` : Nom de la commune
- `Filière` : Électricité ou Gaz
- `Consommation Agriculture (MWh)`
- `Consommation Industrie (MWh)`
- `Consommation Tertiaire (MWh)`
- `Consommation Résidentiel (MWh)`

**Limitations** :
- ❌ Données annuelles uniquement (pas de granularité mensuelle)
- ❌ Certaines communes ont des données masquées (secret statistique)
- ❌ Pas de distinction par type d'énergie dans certains secteurs
- ✅ Couverture nationale exhaustive
- ✅ Données officielles et vérifiées

**Justification** : Jeu de données officiel permettant d'analyser les tendances de consommation énergétique par secteur économique. Complémentaire aux données de qualité de l'air pour une vision complète de l'empreinte environnementale des territoires.

### Upload de données

#### Via l'API
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/upload/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@data/FR_E2_2025-01-01.csv" \
  -F "dataset_type=air_quality" \
  -F "limit=1000"
```

#### Via le script CLI
```powershell
python scripts/upload_csv.py --file data/FR_E2_2025-01-01.csv --type air_quality --limit 100
```

---

## 🛠️ Scripts utilitaires

### `scripts/seed.py`
Peuple la base de données avec des données de test :
- 3 utilisateurs (admin, manager, user)
- 5 zones géographiques
- 4 sources de données
- ~450 indicateurs de démonstration

```powershell
python scripts/seed.py
```

### `scripts/upload_csv.py`
Upload et parse un fichier CSV localement :

```powershell
python scripts/upload_csv.py --file data/example.csv --zone-id 1 --source-id 1 --type air_quality --limit 100
```

Options :
- `--file` : Chemin du fichier CSV (requis)
- `--zone-id` : ID de la zone (optionnel, créée automatiquement sinon)
- `--source-id` : ID de la source (optionnel, créée automatiquement sinon)
- `--type` : Type de dataset (`air_quality` ou `energy_consumption`)
- `--limit` : Nombre maximum de lignes (défaut: 1000)

---

## 🔧 Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine :

```env
# Application
PROJECT_NAME=EcoTrack
VERSION=1.0.0
API_V1_STR=/api/v1

# Security
SECRET_KEY=votre_clé_secrète_très_longue_et_sécurisée
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./ecotrack.db

# CORS (optionnel)
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]
```

### Configuration dans `app/core/config.py`

Les paramètres par défaut sont définis dans `Settings` (Pydantic BaseSettings).

---

## 🔬 Méthodologie de développement

### Phases du projet

1. **Phase 1 - Architecture et authentification** (Semaine 1)
   - Mise en place FastAPI + SQLAlchemy
   - Modèles de données (User, Zone, Source, Indicator)
   - Authentification JWT avec RBAC
   - Tests d'authentification (8 tests)

2. **Phase 2 - CRUD et validation** (Semaine 2)
   - Endpoints CRUD pour toutes les entités
   - Validation Pydantic stricte
   - Filtres avancés et pagination
   - Tests CRUD (23 tests)

3. **Phase 3 - Ingestion de données** (Semaine 3)
   - Parsers CSV pour FR_E2 et consommation énergétique
   - Endpoint d'upload avec détection automatique
   - Script CLI d'import
   - Script de seed pour données de test

4. **Phase 4 - Statistiques et agrégations** (Semaine 4)
   - Endpoints de statistiques (distribution, summary, trend)
   - Calculs d'agrégations optimisés
   - Tests statistiques (6 tests)

5. **Phase 5 - Frontend et finalisations** (Semaine 5)
   - Dashboard web avec Chart.js
   - Interface de login/signup
   - Filtres interactifs et visualisations
   - Documentation complète

### Bonnes pratiques appliquées

✅ **Séparation des responsabilités** : Structure en couches (routes → CRUD → models)  
✅ **Dependency Injection** : Utilisation des dépendances FastAPI pour DB et auth  
✅ **Type hints** : Code entièrement typé pour une meilleure maintenabilité  
✅ **Gestion d'erreurs** : HTTPException avec codes status appropriés  
✅ **Validation** : Pydantic pour validation stricte des entrées/sorties  
✅ **Sécurité** : Hachage bcrypt, JWT, protection RBAC  
✅ **Tests** : 37 tests couvrant auth, CRUD, stats (58% coverage)  
✅ **Documentation** : Swagger UI auto-généré + README détaillé  

---

## 📦 Livrables du projet

### 1. ✅ Dépôt Git complet

**Repository** : [github.com/Slimaaane/EcoTrack-FastAPI](https://github.com/Slimaaane/EcoTrack-FastAPI)

**Contenu** :
- Code API FastAPI (app/)
- Scripts d'ingestion (scripts/)
- Suite de tests pytest (tests/)
- Frontend dashboard (frontend/)
- Configuration et dépendances (requirements.txt, alembic/)
- Documentation (README.md, docstrings)

### 2. ✅ Documentation sur les données

**Fichier** : [Section Sources de données](#sources-de-données) dans ce README

**Contenu** :
- Liste exhaustive des 2 sources externes
- URL et format de chaque source
- Fréquence de mise à jour
- Limitations et contraintes techniques
- Justification des choix

### 3. ✅ Script d'initialisation

**Fichier** : `scripts/seed.py`

**Fonctionnalités** :
```bash
python scripts/seed.py
```
- Création de 3 utilisateurs (admin, manager, user)
- Peuplement de 5 zones géographiques
- Ajout de 4 sources de données
- Insertion de ~450 indicateurs de test
- Données prêtes pour démonstration immédiate

### 4. ✅ Dashboard web

**Fichier** : `frontend/index.html` + `frontend/dashboard.js`

**URL** : http://127.0.0.1:8000/dashboard

**Fonctionnalités** :
- Page de login/signup
- Affichage des indicateurs avec filtres (type, zone, source)
- Graphiques Chart.js (tendances temporelles)
- Cartes statistiques (nombre total zones/sources/indicateurs)
- Gestion des erreurs API
- Interface responsive et intuitive

### 5. ✅ Tests et qualité

**Répertoire** : `tests/`

**Exécution** :
```bash
python -m pytest tests/ --cov=app --cov-report=html
```

**Résultats** :
- 37 tests passés ✅
- 8 tests skipped (fonctionnalités non implémentées)
- 58% de couverture de code
- Rapport HTML dans `htmlcov/index.html`

---

## 📝 License

Ce projet est sous licence MIT.

---

## 👥 Contributeurs

- **Slimaaane** - Développeur principal - EFREI Paris

---

## 🙏 Remerciements

- **EFREI Paris** - Encadrement académique
- [FastAPI](https://fastapi.tiangolo.com/) - Framework web moderne
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM Python
- [data.gouv.fr](https://www.data.gouv.fr/) - Plateforme de données ouvertes
- [Chart.js](https://www.chartjs.org/) - Bibliothèque de graphiques
- [ATMO France](https://atmo-france.org/) - Fédération des organismes de surveillance de la qualité de l'air

---

## 📞 Support

Pour toute question ou problème :
- Ouvrez une [issue GitHub](https://github.com/Slimaaane/EcoTrack-FastAPI/issues)
- Consultez la [documentation API](http://127.0.0.1:8000/docs)

---

**Projet académique EFREI Paris - 2025**  
**Fait avec ❤️ et FastAPI**

