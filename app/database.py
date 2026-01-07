import os
from typing import Generator

from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

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
