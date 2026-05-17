import requests
import uuid
from datetime import datetime


THEMEALDB_CATEGORIES_URL = "https://www.themealdb.com/api/json/v1/1/categories.php"


class FoodCategoryService:
    def get_categories(self):
        response = requests.get(THEMEALDB_CATEGORIES_URL, timeout=30)
        response.raise_for_status()

        raw = response.json().get("categories", [])

        # Transform to match the FoodCategory DB schema
        return [
            {
                "id": uuid.uuid4(),
                "name": item["strCategory"],
                "reference": f"cat-{item['idCategory'].zfill(2)}",
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            for item in raw
        ]


food_category_service = FoodCategoryService()
