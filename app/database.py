from sqlmodel import SQLModel, create_engine, Session
from typing import Generator

DATABASE_URL = "postgresql://items_user:items_password@localhost:5432/items_db"

engine = create_engine(
    DATABASE_URL,
    echo=True,
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
