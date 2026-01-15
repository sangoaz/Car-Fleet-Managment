from fastapi import FastAPI
from sqlmodel import SQLModel
from contextlib import asynccontextmanager

from app.database import engine
from app.routers.vehicule import router as vehicule_router
from app.routers.entretiens import router as entretiens_router
from app.routers.alerts import router as alerts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown (rien à faire pour l'instant)


app = FastAPI(lifespan=lifespan)

app.include_router(vehicule_router)
app.include_router(entretiens_router)
app.include_router(alerts_router)
