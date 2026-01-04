from fastapi import FastAPI
from sqlmodel import SQLModel

from app.database import engine
from app.routers.vehicule import router as vehicule_router
from app.routers.entretiens import router as entretiens_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

app.include_router(vehicule_router)
app.include_router(entretiens_router)