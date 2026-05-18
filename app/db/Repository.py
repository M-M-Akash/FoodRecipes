from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends

from db.Database import get_session
from models.area import Area
from models.meal import Meal
from models.recipe import Recipe


class MealRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_tables(self):
        from db.Database import engine
        from models.base import Base
        import models  # ensure all models are registered with Base metadata
        Base.metadata.create_all(bind=engine)

    def area_exists(self, area_name: str) -> bool:
        return self.session.query(Area).filter_by(id=area_name).first() is not None

    def upsert_area(self, area_name: str) -> None:
        self.session.execute(
            text("""
                MERGE INTO areas dest
                USING (SELECT :id AS id FROM dual) src
                ON (dest.id = src.id)
                WHEN NOT MATCHED THEN
                    INSERT (id) VALUES (:id)
            """),
            {"id": area_name},
        )
        self.session.flush()

    def bulk_upsert_meals(self, meals: list, area_id: str) -> None:
        params = [
            {
                "id": m["idMeal"],
                "name": m["strMeal"],
                "thumbnail_url": m.get("strMealThumb", ""),
                "area_id": area_id,
            }
            for m in meals
        ]
        self.session.execute(
            text("""
                MERGE INTO meals dest
                USING (SELECT :id AS id FROM dual) src
                ON (dest.id = src.id)
                WHEN NOT MATCHED THEN
                    INSERT (id, name, thumbnail_url, area_id)
                    VALUES (:id, :name, :thumbnail_url, :area_id)
            """),
            params,
        )
        self.session.flush()

    def bulk_upsert_recipes(self, meals: list) -> None:
        # :instructions is passed as a direct bind variable (not through USING)
        # to avoid Oracle CLOB restrictions inside SELECT FROM dual subqueries.
        params = [
            {
                "meal_id": m["idMeal"],
                "instructions": m.get("strInstructions", ""),
                "youtube_url": m.get("strYoutube", ""),
            }
            for m in meals
        ]
        self.session.execute(
            text("""
                MERGE INTO recipes dest
                USING (SELECT :meal_id AS meal_id FROM dual) src
                ON (dest.meal_id = src.meal_id)
                WHEN NOT MATCHED THEN
                    INSERT (meal_id, instructions, youtube_url)
                    VALUES (:meal_id, :instructions, :youtube_url)
            """),
            params,
        )

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


def get_meal_repository(session: Session = Depends(get_session)) -> MealRepository:
    return MealRepository(session)
