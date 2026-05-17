from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from helpers.env import connect_db
from db.Database import  Area, Meal, Recipe
from sqlalchemy.orm import joinedload


# class FoodRepository:
#     def __init__(self) -> None:
#         self.engine = connect_db()
#         self.Session = sessionmaker(bind=self.engine)
#         self.session = self.Session()
    
#     def create_migration_table(self):
#         FoodCategory.__table__.create(bind=self.engine, checkfirst=True)

#     def insert_data(self, bulk_data):
#         nls_timestamp_format_sql = text("ALTER SESSION SET NLS_TIMESTAMP_FORMAT = 'YYYY-MM-DD HH24:MI:SS'")
#         try:
#             self.session.execute(nls_timestamp_format_sql)
#             self.session.bulk_insert_mappings(FoodCategory, bulk_data)
#             self.session.commit()

#         except Exception as e:
#             print(f"Error: {str(e)}")

#     def count(self):
#         return self.session.query(FoodCategory).count()

#     def get_all_data(self):
#         return self.session.query(FoodCategory).all()

#     def drop_table(self):
#         FoodCategory.__table__.drop(self.engine)


class MealRepository:
    def __init__(self) -> None:
        self.engine = connect_db()
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def create_tables(self):
        Area.__table__.create(bind=self.engine, checkfirst=True)
        Meal.__table__.create(bind=self.engine, checkfirst=True)
        Recipe.__table__.create(bind=self.engine, checkfirst=True)

    def area_exists(self, area_name: str) -> bool:
        return self.session.query(Area).filter_by(id=area_name).first() is not None

    def insert_area(self, area_name: str):
        self.session.add(Area(id=area_name))
        self.session.flush()

    def bulk_insert_meals(self, meals: list, area_id: str):
        mappings = [
            {
                "id": m["idMeal"],
                "name": m["strMeal"],
                "thumbnail_url": m.get("strMealThumb", ""),
                "area_id": area_id,
            }
            for m in meals
        ]
        self.session.bulk_insert_mappings(Meal, mappings)
        self.session.flush()

    def bulk_insert_recipes(self, meals: list):
        mappings = [
            {
                "meal_id": m["idMeal"],
                "instructions": m.get("strInstructions", ""),
                "youtube_url": m.get("strYoutube", ""),
            }
            for m in meals
        ]
        self.session.bulk_insert_mappings(Recipe, mappings)

    def get_meals_by_area(self, area_name: str):
        return self.session.query(Meal).filter_by(area_id=area_name).all()

    def get_meals_with_recipes(self, area_name: str):
        
        return (
            self.session.query(Meal)
            .options(joinedload(Meal.recipe))
            .filter_by(area_id=area_name)
            .all()
        )

    def commit(self):
        self.session.commit()