from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.api.endpoints import auth, users, zones, sources, indicators, stats, ingest, upload
import os

# Créer l'application FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    debug=settings.DEBUG
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routeurs API
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(zones.router, prefix=f"{settings.API_V1_PREFIX}/zones", tags=["Zones"])
app.include_router(sources.router, prefix=f"{settings.API_V1_PREFIX}/sources", tags=["Sources"])
app.include_router(indicators.router, prefix=f"{settings.API_V1_PREFIX}/indicators", tags=["Indicators"])
app.include_router(stats.router, prefix=f"{settings.API_V1_PREFIX}/stats", tags=["Statistics"])
app.include_router(ingest.router, prefix=f"{settings.API_V1_PREFIX}/ingest", tags=["Data Ingestion"])
app.include_router(upload.router, prefix=f"{settings.API_V1_PREFIX}/upload", tags=["CSV Upload"])

# Servir les fichiers statiques du frontend
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")
    
    @app.get("/dashboard")
    async def dashboard():
        """Page du tableau de bord."""
        return FileResponse(os.path.join(frontend_path, "index.html"))


@app.get("/")
async def root():
    """Point d'entrée racine de l'API."""
    return {
        "message": "Bienvenue sur EcoTrack API",
        "version": "0.1.0",
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get("/health")
async def health_check():
    """Endpoint de vérification de santé de l'API."""
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME
    }


@app.get("/ping")
async def ping():
    """Endpoint de test simple."""
    return {"message": "pong"}
