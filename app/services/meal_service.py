import httpx
import asyncio
from fastapi import Depends
from fastapi.concurrency import run_in_threadpool

from db.Repository import MealRepository, get_meal_repository
from core.logging import logger

BASE_URL = "https://www.themealdb.com/api/json/v1/1"

# Caps concurrent recipe fetches — polite to the free API, still much faster than sequential
_SEMAPHORE: asyncio.Semaphore | None = None


def _get_semaphore() -> asyncio.Semaphore:
    global _SEMAPHORE
    if _SEMAPHORE is None:
        _SEMAPHORE = asyncio.Semaphore(5)
    return _SEMAPHORE


class MealApiClient:
    """
    Handles all external TheMealDB API calls.
    Module-level singleton — no DB dependency, cache persists across requests.
    """
    _areas_cache: list | None = None

    def get_all_areas(self) -> list:
        if MealApiClient._areas_cache is None:
            response = httpx.get(f"{BASE_URL}/list.php?a=list", timeout=30)
            response.raise_for_status()
            MealApiClient._areas_cache = [
                a["strArea"] for a in (response.json().get("meals") or [])
            ]
            logger.info(f"Fetched {len(MealApiClient._areas_cache)} areas from API")
        return MealApiClient._areas_cache

    async def get_meals_by_area(self, area: str) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/filter.php?a={area}", timeout=30)
            response.raise_for_status()
        return response.json().get("meals") or []


# Module-level singleton — shared across all requests
api_client = MealApiClient()


async def _fetch_recipes_parallel(meals_data: list) -> list:
    """Fetch all recipe details in parallel using a shared client, capped at 5 concurrent."""
    semaphore = _get_semaphore()

    async def fetch_one(meal_id: str, client: httpx.AsyncClient) -> dict | None:
        async with semaphore:
            await asyncio.sleep(0.3)  # be polite to the free API
            response = await client.get(f"{BASE_URL}/lookup.php?i={meal_id}", timeout=30)
            response.raise_for_status()
            meals = response.json().get("meals") or []
            return meals[0] if meals else None

    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            *[fetch_one(m["idMeal"], client) for m in meals_data]
        )

    return [r for r in results if r is not None]


class MealService:
    """
    Business logic layer.
    Receives a MealRepository via dependency injection — never creates DB connections itself.
    """

    def __init__(self, repo: MealRepository):
        self.repo = repo

    def _save_to_db(self, area: str, full_meals: list) -> None:
        """All DB writes grouped into one sync call so they run on a single thread."""
        self.repo.upsert_area(area)
        self.repo.bulk_upsert_meals(full_meals, area)
        self.repo.bulk_upsert_recipes(full_meals)
        self.repo.commit()

    async def get_or_fetch_meals(self, area: str) -> list | None:
        """
        Return meals for an area from the DB if already stored,
        otherwise fetch from the API in parallel, persist, then return.
        Returns None if no meals are found for the given area.
        """
        await run_in_threadpool(self.repo.create_tables)

        if not await run_in_threadpool(self.repo.area_exists, area):
            logger.info(f"'{area}' not in DB — fetching from API")
            meals_data = await api_client.get_meals_by_area(area)

            if not meals_data:
                return None

            full_meals = await _fetch_recipes_parallel(meals_data)

            if not full_meals:
                return None

            await run_in_threadpool(self._save_to_db, area, full_meals)
            logger.info(f"Saved {len(full_meals)} meals for '{area}'")
        else:
            logger.info(f"'{area}' loaded from DB")

        return await run_in_threadpool(self.repo.get_meals_with_recipes, area)


def get_meal_service(repo: MealRepository = Depends(get_meal_repository)) -> MealService:
    return MealService(repo)
