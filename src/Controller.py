from db.Repository import FoodRepository
from services.foodics_service import food_category_service


repository = FoodRepository()
repository.create_migration_table()

if repository.count() == 0:
    print("No data found — seeding from API...")
    categories = food_category_service.get_categories()
    repository.insert_data(bulk_data=categories)
else:
    print(f"Already seeded ({repository.count()} rows). Skipping insert.")

all_data = repository.get_all_data()
for row in all_data:
    print(row.name)