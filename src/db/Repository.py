from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from helpers.env import connect_db
from db.Database import FoodCategory

class FoodRepository:
    def __init__(self) -> None:
        self.engine = connect_db()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
    
    def create_migration_table(self):
        FoodCategory.__table__.create(bind=self.engine, checkfirst=True)

    def insert_data(self, bulk_data):
        nls_timestamp_format_sql = text("ALTER SESSION SET NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")
        try:
            self.session.execute(nls_timestamp_format_sql)
            self.session.bulk_insert_mappings(FoodCategory, bulk_data)
            self.session.commit()

        except Exception as e:
            print(f"Error: {str(e)}")

    def count(self):
        return self.session.query(FoodCategory).count()

    def get_all_data(self):
        return self.session.query(FoodCategory).all()

    def drop_table(self):
        FoodCategory.__table__.drop(self.engine)