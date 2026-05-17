import requests
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.meal_service import meal_service

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _render(request: Request, **ctx):
    return templates.TemplateResponse("index.html", {"request": request, **ctx})


def _areas():
    try:
        return meal_service.get_all_areas()
    except Exception:
        return []


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return _render(request, areas=_areas())


@router.get("/search", response_class=HTMLResponse)
def search(request: Request, area: str = ""):
    area = area.strip()
    areas = _areas()

    if not area:
        return _render(request, areas=areas)

    try:
        meals = meal_service.get_or_fetch_meals(area)

        if meals is None:
            return _render(request, areas=areas, query=area,
                           error=f"No recipes found for '{area}'.")

        return _render(request, areas=areas, meals=meals, query=area)

    except requests.RequestException:
        return _render(request, areas=areas, query=area,
                       error="Could not reach the recipe API. Please try again later.")
    except Exception as e:
        return _render(request, areas=areas, query=area,
                       error=f"Something went wrong: {e}")
