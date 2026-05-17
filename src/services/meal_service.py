import requests
import time
from fastapi import Depends

from db.Repository import MealRepository, get_meal_repository
from core.logging import logger

BASE_URL = "https://www.themealdb.com/api/json/v1/1"


class MealApiClient:
    """
    Handles all external TheMealDB API calls.
    Module-level singleton — no DB dependency, cache persists across requests.
    """
    _areas_cache: list | None = None

    def get_all_areas(self) -> list:
        if MealApiClient._areas_cache is None:
            response = requests.get(f"{BASE_URL}/list.php?a=list", timeout=30)
            response.raise_for_status()
            MealApiClient._areas_cache = [
                a["strArea"] for a in (response.json().get("meals") or [])
            ]
            logger.info(f"Fetched {len(MealApiClient._areas_cache)} areas from API")
        return MealApiClient._areas_cache

    def get_meals_by_area(self, area: str) -> list:
        response = requests.get(f"{BASE_URL}/filter.php?a={area}", timeout=30)
        response.raise_for_status()
        return response.json().get("meals") or []

    def get_recipe(self, meal_id: str) -> dict | None:
        time.sleep(0.3)  # be polite to the free API
        response = requests.get(f"{BASE_URL}/lookup.php?i={meal_id}", timeout=30)
        response.raise_for_status()
        meals = response.json().get("meals") or []
        return meals[0] if meals else None


# Module-level singleton — shared across all requests
api_client = MealApiClient()


class MealService:
    """
    Business logic layer.
    Receives a MealRepository via dependency injection — never creates DB connections itself.
    """

    def __init__(self, repo: MealRepository):
        self.repo = repo

    def get_or_fetch_meals(self, area: str) -> list | None:
        """
        Return meals for an area from the DB if already stored,
        otherwise fetch from the API, persist, then return.
        Returns None if no meals are found for the given area.
        """
        self.repo.create_tables()

        if not self.repo.area_exists(area):
            logger.info(f"'{area}' not in DB — fetching from API")
            meals_data = api_client.get_meals_by_area(area)

            full_meals = []
            for meal_data in meals_data:
                full_data = api_client.get_recipe(meal_data["idMeal"])
                if full_data:
                    full_meals.append(full_data)

            if not full_meals:
                return None

            self.repo.insert_area(area)
            self.repo.bulk_insert_meals(full_meals, area)
            self.repo.bulk_insert_recipes(full_meals)
            self.repo.commit()
            logger.info(f"Saved {len(full_meals)} meals for '{area}'")
        else:
            logger.info(f"'{area}' loaded from DB")

        return self.repo.get_meals_with_recipes(area)


def get_meal_service(repo: MealRepository = Depends(get_meal_repository)) -> MealService:
    return MealService(repo)
