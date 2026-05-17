from sqlalchemy import create_engine
from core.config import settings


def connect_db():
    return create_engine(settings.db_url)
