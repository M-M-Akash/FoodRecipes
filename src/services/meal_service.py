import requests
import time

BASE_URL = "https://www.themealdb.com/api/json/v1/1"


class MealService:
    def get_meals_by_area(self, area: str) -> list:
        """Fetch meal list for a given cuisine area (e.g. 'Mexican', 'Italian')."""
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


meal_service = MealService()
