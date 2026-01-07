""" Schémas pydantic (input / output API) """
from pydantic import BaseModel
from datetime import date
from typing import List, Optional
from app.enums import EntretienType

# Creation d'un véhicule
class Create_vehicule(BaseModel):
    plate: str
    model: str
    km: int
    buy_date: date | None = None
    first_registration_date: date | None = None

# Modification des infos d'un véhicule
class Update_vehicule(BaseModel):
    plate: str | None = None
    model: str | None = None
    km: int | None = None
    buy_date: date | None = None
    first_registration_date: date | None = None

# Creation d'un entretien de véhicule
class Create_entretien(BaseModel):
    date: date
    km: int
    type: str
    cost: float | None = None
    comment: str | None = None


class EntretienOverview(BaseModel):
    id: int
    date: date
    km: int
    type: EntretienType
    cost: float | None = None
    comment: str | None = None


class VehiculeOverview(BaseModel):
    id: int
    plate: str
    model: str
    km: int


class VehiculeOverviewResponse(BaseModel):
    vehicule: VehiculeOverview
    last_entretiens: List[EntretienOverview]
    last_controle_technique: Optional[EntretienOverview]