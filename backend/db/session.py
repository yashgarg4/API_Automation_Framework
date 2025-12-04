from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.core.config import get_settings

settings = get_settings()

# For SQLite, need check_same_thread=False when using with FastAPI
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
