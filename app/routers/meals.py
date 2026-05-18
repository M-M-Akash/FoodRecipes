import httpx
from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.meal_service import MealService, get_meal_service, api_client

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def _render(request: Request, **ctx):
    return templates.TemplateResponse("index.html", {"request": request, **ctx})


def _areas():
    try:
        return api_client.get_all_areas()
    except Exception:
        return []


@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return _render(request, areas=_areas())


@router.get("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    area: str = "",
    service: MealService = Depends(get_meal_service),
):
    area = area.strip()
    areas = _areas()

    if not area:
        return _render(request, areas=areas)

    try:
        meals = await service.get_or_fetch_meals(area)

        if meals is None:
            return _render(request, areas=areas, query=area,
                           error=f"No recipes found for '{area}'.")

        return _render(request, areas=areas, meals=meals, query=area)

    except httpx.RequestError:
        return _render(request, areas=areas, query=area,
                       error="Could not reach the recipe API. Please try again later.")
    except Exception as e:
        return _render(request, areas=areas, query=area,
                       error=f"Something went wrong: {e}")
