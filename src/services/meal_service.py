import requests
import time

from db.Repository import MealRepository

BASE_URL = "https://www.themealdb.com/api/json/v1/1"


class MealService:
    def __init__(self):
        self._areas_cache = None

    def get_all_areas(self) -> list:
        """Fetch and cache the list of all valid cuisine areas."""
        if self._areas_cache is None:
            response = requests.get(f"{BASE_URL}/list.php?a=list", timeout=30)
            response.raise_for_status()
            self._areas_cache = [
                a["strArea"] for a in (response.json().get("meals") or [])
            ]
        return self._areas_cache

    def get_meals_by_area(self, area: str) -> list:
        """Fetch meal list for a given cuisine area from the external API."""
        response = requests.get(f"{BASE_URL}/filter.php?a={area}", timeout=30)
        response.raise_for_status()
        return response.json().get("meals") or []

    def get_recipe(self, meal_id: str) -> dict | None:
        """Fetch full meal details including recipe instructions by meal ID."""
        time.sleep(0.3)  # be polite to the free API
        response = requests.get(f"{BASE_URL}/lookup.php?i={meal_id}", timeout=30)
        response.raise_for_status()
        meals = response.json().get("meals") or []
        return meals[0] if meals else None

    def get_or_fetch_meals(self, area: str) -> list | None:
        """
        Return meals for an area from the DB if already stored,
        otherwise fetch from the API, persist, then return.
        Returns None if no meals are found for the given area.
        """
        repo = MealRepository()
        repo.create_tables()

        if not repo.area_exists(area):
            meals_data = self.get_meals_by_area(area)

            full_meals = []
            for meal_data in meals_data:
                full_data = self.get_recipe(meal_data["idMeal"])
                if full_data:
                    full_meals.append(full_data)

            if not full_meals:
                return None

            repo.insert_area(area)
            repo.bulk_insert_meals(full_meals, area)
            repo.bulk_insert_recipes(full_meals)
            repo.commit()

        return repo.get_meals_with_recipes(area)


meal_service = MealService()
