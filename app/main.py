from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from app.database import engine
from app.routers.vehicule import router as vehicule_router
from app.routers.entretiens import router as entretiens_router
from app.routers.alerts import router as alerts_router
from app.routers.fuel import router as fuel_router
from app.routers.company import router as company_router
from app.routers.users import router as users_router
from app.routers.vehicule_assignement import router as assignement_router

# ---------------------------------------------------------
# Point d'entrée de l'application FastAPI
#
# Ce fichier initialise l'application, configure son cycle
# de vie (démarrage / arrêt) et enregistre les routes API.
#
# La fonction `lifespan` est utilisée pour exécuter du code
# au démarrage de l'application, notamment l'initialisation
# de la base de données (création des tables si nécessaires).
#
# Le détail du fonctionnement interne de FastAPI n'est pas
# requis ici : ce fichier sert principalement à brancher
# les différents composants de l'application.
# ---------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown (rien à faire pour l'instant)


app = FastAPI(lifespan=lifespan)


# Branchement des différentes routes du dossier /routers
app.include_router(vehicule_router)
app.include_router(entretiens_router)
app.include_router(alerts_router)
app.include_router(fuel_router)
app.include_router(company_router)
app.include_router(users_router)
app.include_router(assignement_router)
