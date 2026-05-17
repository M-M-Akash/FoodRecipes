import requests
from unittest.mock import patch, MagicMock


def test_index_renders(client):
    with patch("routers.meals.api_client") as mock_api:
        mock_api.get_all_areas.return_value = ["Mexican", "Italian"]
        response = client.get("/")
    assert response.status_code == 200
    assert "Mexican" in response.text
    assert "Italian" in response.text


def test_search_returns_meals(client_with_mock_service):
    client, mock_service = client_with_mock_service
    mock_meal = MagicMock()
    mock_meal.name = "Tacos"
    mock_meal.thumbnail_url = None
    mock_meal.recipe = MagicMock()
    mock_meal.recipe.instructions = "Cook the tacos."
    mock_meal.recipe.youtube_url = None
    mock_service.get_or_fetch_meals.return_value = [mock_meal]

    with patch("routers.meals.api_client") as mock_api:
        mock_api.get_all_areas.return_value = ["Mexican"]
        response = client.get("/search?area=Mexican")

    assert response.status_code == 200
    assert "Tacos" in response.text
    mock_service.get_or_fetch_meals.assert_called_once_with("Mexican")


def test_search_no_results(client_with_mock_service):
    client, mock_service = client_with_mock_service
    mock_service.get_or_fetch_meals.return_value = None

    with patch("routers.meals.api_client") as mock_api:
        mock_api.get_all_areas.return_value = ["Mexican"]
        response = client.get("/search?area=Mexican")

    assert response.status_code == 200
    assert "No recipes found" in response.text


def test_search_empty_area(client):
    with patch("routers.meals.api_client") as mock_api:
        mock_api.get_all_areas.return_value = ["Mexican", "Italian"]
        response = client.get("/search?area=")
    assert response.status_code == 200
    # No query submitted — just the dropdown rendered
    assert "Mexican" in response.text


def test_search_api_error(client_with_mock_service):
    client, mock_service = client_with_mock_service
    mock_service.get_or_fetch_meals.side_effect = requests.RequestException("API down")

    with patch("routers.meals.api_client") as mock_api:
        mock_api.get_all_areas.return_value = []
        response = client.get("/search?area=Mexican")

    assert response.status_code == 200
    assert "Could not reach" in response.text
