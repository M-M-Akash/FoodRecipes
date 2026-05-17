from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings

engine = create_engine(settings.db_url)
SessionLocal = sessionmaker(bind=engine)


def get_session():
    """FastAPI dependency that yields a DB session and closes it after the request."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
