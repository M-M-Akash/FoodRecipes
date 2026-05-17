import os
import sys
from db.Repository import MealRepository
from services.meal_service import meal_service


def main():
    # Accept area from: env var (Docker), CLI arg, or interactive prompt
    area = (
        os.getenv("AREA")
        or (sys.argv[1] if len(sys.argv) > 1 else None)
        or input("Enter cuisine area (e.g. Mexican, Italian, Japanese): ").strip()
    )

    if not area:
        print("No area provided. Exiting.")
        return

    repo = MealRepository()
    repo.create_tables()

    if repo.area_exists(area):
        print(f"'{area}' is already in the database. Loading from DB...\n")
        meals = repo.get_meals_by_area(area)
        for meal in meals:
            print(f"  - {meal.name}")
        print(f"\n{len(meals)} meals found.")
        return

    print(f"Fetching meals for '{area}' from API...")
    meals_data = meal_service.get_meals_by_area(area)

    if not meals_data:
        print(f"No meals found for '{area}'. Check the area name and try again.")
        return

    print(f"Found {len(meals_data)} meals. Fetching recipes (this may take a moment)...\n")

    repo.insert_area(area)

    # Fetch all recipes first, then bulk insert in one shot
    full_meals = []
    for meal_data in meals_data:
        full_data = meal_service.get_recipe(meal_data["idMeal"])
        if full_data:
            full_meals.append(full_data)
            print(f"  + {full_data['strMeal']}")

    repo.bulk_insert_meals(full_meals, area)
    repo.bulk_insert_recipes(full_meals)
    repo.commit()
    print(f"\nDone! {len(full_meals)} meals and recipes saved for '{area}'.")



if __name__ == "__main__":
    main()
