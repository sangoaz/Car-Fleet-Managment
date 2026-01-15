"""Modèles SQLModel"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import date
from typing import List, Optional

from app.enums import EntretienType


# Table des Véhicules
class Vehicule(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    plate: str
    model: str
    km: int

    buy_date: date | None = Field(default=None)
    first_registration_date: date | None = Field(default=None)

    entretiens: List["Entretien"] = Relationship(back_populates="vehicule")


# Table des Entretiens
class Entretien(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    vehicule_id: int = Field(foreign_key="vehicule.id")
    vehicule: Optional[Vehicule] = Relationship(back_populates="entretiens")

    date: date
    km: int
    type: EntretienType  # Vidange / Pneus / CT, etc...
    cost: float | None = None
    comment: str | None = None


# Table des pleins de carburant
class FuelFill(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    vehicule_id: int = Field(foreign_key="vehicule.id")

    date: date
    km: int
    liters: float
    cost: float | None = None


# Table des incidents

# Table des réparations
