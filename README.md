# Food Recipes

A portfolio web app that fetches meal recipes from [TheMealDB](https://www.themealdb.com/) free API, stores them in an Oracle database, and displays them through a FastAPI web interface.

![App screenshot](assets/Screenshot%20From%202026-05-18%2002-44-51.png)

## What it does

- Browse recipes by cuisine area (Mexican, Italian, Japanese, etc.)
- First search for an area fetches all recipe details from TheMealDB **in parallel** (up to 5 concurrent requests) and bulk-upserts them into Oracle — subsequent searches load instantly from the DB
- Displays meal name, thumbnail, instructions, and a YouTube link per recipe

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI with Jinja2 templates |
| Database | Oracle XE 21c (via Docker) |
| ORM | SQLAlchemy 2.0 |
| DB driver | `oracledb` thin mode (no Oracle Client required) |
| Config | Pydantic Settings |
| Containerisation | Docker + Docker Compose |
| Testing | pytest + HTTPX |
| External API | TheMealDB (free, no API key) |

## Project Structure

```
app/
├── core/           # App-wide config (Pydantic Settings) and logging
├── models/         # SQLAlchemy ORM models (Area, Meal, Recipe)
├── schemas/        # Pydantic response schemas
├── db/             # Engine, session factory, and DB connection
├── routers/        # FastAPI route handlers
├── services/       # Business logic + external API client
└── helpers/        # DB connection helper
tests/
└── routers/        # Route-level tests with mocked dependencies
```

## Running locally

**Prerequisites:** Docker and Docker Compose

1. Copy the example env file:
   ```bash
   cp .env.example .env
   ```
2. Start everything:
   ```bash
   docker compose up --build
   ```
3. Open [http://localhost:8000](http://localhost:8000)

The Oracle container takes ~90 seconds on first start. The app waits for it via a healthcheck.

## Running tests

Tests run inside the app container (no local Python environment needed):

```bash
sudo docker compose run --no-deps --rm \
  -v "$(pwd)/tests:/app/tests" \
  -v "$(pwd)/pytest.ini:/app/pytest.ini" \
  app python -m pytest tests/ -v
```

`--no-deps` skips starting the Oracle DB since all tests mock the data layer.

## How first-search fetching works

When an area is not yet in the database:

1. The route handler (`async def search`) fetches the list of meals for that area from TheMealDB
2. All individual recipe detail requests are fired **concurrently** using `asyncio.gather` with an `asyncio.Semaphore(5)` cap — this replaces the old sequential loop with a `time.sleep(0.3)` per meal
3. The synchronous SQLAlchemy writes run in FastAPI's thread pool via `run_in_threadpool`, keeping the async event loop unblocked
4. Each insert uses an Oracle **MERGE** statement (`WHEN NOT MATCHED THEN INSERT`) instead of a plain `INSERT` — this means two concurrent requests for the same uncached area cannot cause a primary key violation; the second write is silently a no-op

