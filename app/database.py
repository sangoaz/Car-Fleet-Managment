from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

DATABASE_URL = "postgresql://fleet_user:fleet_password@localhost:5432/fleet_db"


engine = create_engine(
    DATABASE_URL,
    echo=True,
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
