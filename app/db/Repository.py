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


def get_meal_repository(session: Session = Depends(get_session)) -> MealRepository:
    return MealRepository(session)
