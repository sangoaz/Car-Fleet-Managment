import os
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

# ---------------------------------------------------------
# Configuration de la base de données
#
# Ce fichier définit :
# - l'engine : point d'accès global à la base de données
# - la fonction get_session : fourniture d'une session
#   temporaire et isolée pour chaque requête API
#
# L'engine est créé une seule fois et partagé dans toute
# l'application. Les sessions, elles, sont courtes et
# automatiquement ouvertes et fermées grâce à l'utilisation
# de `yield`, ce qui évite les fuites de connexions.
#
# Ce fichier ne contient aucune logique métier.
# ---------------------------------------------------------

# Charge le fichier .env
load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set. Check your environment variables.")

engine = create_engine(
    DATABASE_URL,
    echo=True,
)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
