import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

from main import app
from services.meal_service import get_meal_service, MealService


def make_mock_meal(name: str) -> MagicMock:
    meal = MagicMock()
    meal.name = name
    meal.thumbnail_url = f"https://example.com/{name.lower()}.jpg"
    meal.recipe = MagicMock()
    meal.recipe.instructions = f"Instructions for {name}"
    meal.recipe.youtube_url = "https://youtube.com/watch?v=test"
    return meal


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_service():
    return MagicMock(spec=MealService)


@pytest.fixture
def client_with_mock_service(mock_service):
    app.dependency_overrides[get_meal_service] = lambda: mock_service
    yield TestClient(app), mock_service
    app.dependency_overrides.clear()
