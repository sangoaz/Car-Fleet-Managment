""" Schémas pydantic (input / output API) """
from pydantic import BaseModel
from datetime import date

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