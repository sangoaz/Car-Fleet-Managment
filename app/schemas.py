"""Schémas pydantic (input / output API)"""

from pydantic import BaseModel, ConfigDict
from datetime import date as Date
from typing import List, Optional
from app.enums import EntretienType
from app.services.alerts.base import Alert


# =========================
# VEHICULE
# =========================


# Creation d'un véhicule
class Create_vehicule(BaseModel):
    plate: str
    model: str
    km: int
    buy_date: Date | None = None
    first_registration_date: Date | None = None


# Modification des infos d'un véhicule
class Update_vehicule(BaseModel):
    plate: str | None = None
    model: str | None = None
    km: int | None = None
    buy_date: Date | None = None
    first_registration_date: Date | None = None


class VehiculeRead(BaseModel):
    id: int
    plate: str
    model: str
    km: int

    model_config = ConfigDict(from_attributes=True)


# =========================
# ENTRETIEN
# =========================


# Creation d'un entretien de véhicule
class Create_entretien(BaseModel):
    date: Date
    km: int
    type: EntretienType
    cost: float | None = None
    comment: str | None = None


class EntretienRead(BaseModel):
    id: int
    date: Date
    km: int
    type: EntretienType
    cost: float | None = None
    comment: str | None = None

    model_config = ConfigDict(from_attributes=True)


# Modification des infos d'un entretien
class Update_entretien(BaseModel):
    date: Date | None = None
    km: int | None = None
    type: EntretienType | None = None
    cost: float | None = None
    comment: str | None = None


# =========================
# PAGINATION
# =========================


class PaginatedEntretiens(BaseModel):
    total_count: int
    items: List[EntretienRead]


# =========================
# OVERVIEW VEHICULE
# =========================


# Affichage d'un entretien
class EntretienOverview(BaseModel):
    id: int
    date: Date
    km: int
    type: EntretienType
    cost: float | None = None
    comment: str | None = None

    model_config = ConfigDict(from_attributes=True)


# Affichage d'un véhicule
class VehiculeOverview(BaseModel):
    id: int
    plate: str
    model: str
    km: int

    model_config = ConfigDict(from_attributes=True)


class EntretienIssue(BaseModel):
    type: EntretienType
    issue: str
    details: str


# Affichage de l'overview du véhicule
class VehiculeOverviewResponse(BaseModel):
    vehicule: VehiculeOverview
    last_entretiens: List[EntretienOverview]
    last_controle_technique: Optional[EntretienOverview]
    issues: List[EntretienIssue] = []


# =========================
# ALERTES
# =========================


class VehiculeAlertsResponse(BaseModel):
    vehicule_id: int
    alerts: List[Alert]


# =========================
# PLEINS DE CARBURANT
# =========================


class FuelFillCreate(BaseModel):
    date: Date
    km: int
    liters: float
    cost: float


class FuelFillRead(BaseModel):
    id: int
    vehicule_id: int
    date: Date
    km: int
    liters: float
    cost: float

    model_config = ConfigDict(from_attributes=True)


class FuelFillUpdate(BaseModel):
    date: Date | None = None
    km: int | None = None
    liters: float | None = None
    cost: float | None = None


class FuelStatsRead(BaseModel):
    total_km: int
    total_liters: float
    total_cost: float

    average_consumption: float | None
    last_consumption: float | None
    rolling_consumption: float | None
    cost_per_km: float | None
