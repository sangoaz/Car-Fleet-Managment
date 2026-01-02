""" Schémas pydantic (input / output API) """
from typing import Optional
from pydantic import BaseModel
from datetime import date

# Creation d'un véhicule
class Create_vehicule(BaseModel):
    plate: str
    model: str
    km: int
    buy_date: Optional[date] = None
    first_registration_date: Optional[date] = None

