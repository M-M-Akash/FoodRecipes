import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine

load_dotenv(find_dotenv())
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT", "1521")
sid = os.getenv("DB_SID")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")

def connect_db():
    connection_url = f"oracle+oracledb://{user}:{password}@{host}:{port}/{sid}"
    engine = create_engine(connection_url)
    return engine