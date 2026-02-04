"""Modèles SQLModel"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import date, datetime
from typing import List, Optional

from app.enums import EntretienType, UserRole

# ---------------------------------------------------------
# Modèles de données (SQLModel)
#
# Ce fichier définit les entités principales de l'application
# et leur structure en base de données :
# - Vehicule : représente un véhicule de la flotte
# - Entretien : représente un entretien lié à un véhicule
# - FuelFill : représente un plein de carburant
# - User : représente les utilisateurs
# - Company : représente les entreprises
#
# Les clés étrangères (foreign_key) définissent les relations
# au niveau de la base de données.
#
# Les Relationship sont utilisées uniquement pour faciliter
# la navigation entre les objets Python (ex: vehicule.entretiens)
# et n'ont pas d'impact direct sur la structure des tables SQL.
#
# Certaines relations sont optionnelles côté Python car elles
# peuvent ne pas être chargées en mémoire selon les requêtes,
# même si elles sont obligatoires au niveau métier.
# ---------------------------------------------------------


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


# Table des utilisateurs
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str | None = None
    password_hash: str
    role: UserRole = Field(default=UserRole.DRIVER)
    is_active: bool = Field(default=True)
    company_id: int | None = Field(default=None, foreign_key="company.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Table des entreprises
class Company(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)

    name: str = Field(index=True)
    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)


# Table des incidents

# Table des réparations
