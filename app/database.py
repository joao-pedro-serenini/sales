"""Engine do banco de dados, sessão e modelo base."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config import DATABASE_URL

connect_args: dict[str, bool] = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Base declarativa para todos os modelos ORM."""


def get_db() -> Generator[Session, None, None]:
    """Fornece uma sessão do banco de dados e garante que ela seja fechada após o uso."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
