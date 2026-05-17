# Food Recipes

A portfolio web app that fetches meal recipes from [TheMealDB](https://www.themealdb.com/) free API, stores them in an Oracle database, and displays them through a FastAPI web interface.

![App screenshot](assets/Screenshot%20From%202026-05-18%2002-44-51.png)

## What it does

- Browse recipes by cuisine area (Mexican, Italian, Japanese, etc.)
- First search fetches from the API and bulk-inserts meals and recipes into Oracle in a single operation — subsequent searches load from the DB
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

Install dependencies and run pytest from the project root:

```bash
pip install -r requirements.txt
pytest
```

