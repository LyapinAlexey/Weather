# Weather

Production-grade weather application with a Flask web interface and CLI tool, built as a portfolio project demonstrating real-world engineering practices.

![CI](https://github.com/LyapinAlexey/Weather/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![codecov](https://codecov.io/github/LyapinAlexey/Weather/graph/badge.svg?token=VIAZVWQ81B)](
  https://codecov.io/github/LyapinAlexey/Weather
)

## Features

- 🌦 Current weather + 3-day forecast via [WeatherAPI](https://www.weatherapi.com/)
- 🖥 Web interface (Flask) and CLI tool, sharing a common service/model layer
- 📍 Automatic city detection by IP (with fallback chain: ip-api.com → ipinfo.io)
- 🗄 PostgreSQL persistence via SQLAlchemy + Alembic migrations
- ✅ Input validation with Marshmallow
- 🚦 Rate limiting (flask-limiter)
- 🐳 Fully containerized with Docker Compose
- 🔄 CI pipeline via GitHub Actions (build, migrate, health check)
- 🧪 45+ automated tests (pytest): unit, mocked service, Flask route, and real PostgreSQL integration tests

### Tech Stack

- **Backend:** `Python 3.13`, `Flask`, `Gunicorn`, `SQLAlchemy`, `Alembic`, `Marshmallow`, `Flask-Limiter`
- **Database:** `PostgreSQL`
- **Infrastructure & DevOps:** `Docker`, `Docker Compose`, `GitHub Actions (CI/CD)`
- **Testing & Quality:** `Pytest`, `unittest.mock`, `Codecov`

## Quick Start (Docker)

1. Clone the repo and copy the environment template:
```bash
   cp .env.example .env
```
2. Fill in `.env` — at minimum you'll need a free API key from [weatherapi.com](https://www.weatherapi.com/) (`WEATHER_API_KEY`) and a `SECRET_KEY`:
```bash
   python -c "import secrets; print(secrets.token_hex(32))"
```
3. Start the stack:
```bash
   docker compose up -d
   docker compose run --rm cli alembic upgrade head
```
4. Open [http://localhost:5001](http://localhost:5001)

## Running the CLI

```bash
docker compose run --rm cli python main.py
```

## Running Tests

Tests require a dedicated PostgreSQL test container (kept separate from the dev/prod database):

```bash
docker compose up -d weather_test_db
DATABASE_URL="postgresql://test_user:test_password@localhost:5433/test_weather_db" alembic upgrade head
pytest -v
```

## Project Architecture

```mermaid
graph TD
    %% Interfaces & Entrypoints
    Client([Client / Browser]) -->|HTTP / Gunicorn| Web[WEB / Flask App]
    CLIUser([Administrator]) -->|Command Line| CLI[CLI / main.py]

    %% Shared Application Layer
    subgraph AppLayer [Shared Modules & Business Logic]
        Web & CLI --> Services[services.py: Weather, Geolocation & Rate Limiting]
        Web & CLI --> Schemas[schemas.py: Marshmallow Validation]
        Web & CLI --> Models[models.py: SQLAlchemy ORM]

        Services --> WeatherAPI[WeatherAPI.com]
        Services --> IPAPI[ip-api.com / ipinfo.io]
    end

    %% Data & Migrations Layer
    subgraph DataLayer [Data Management]
        Models --> Alembic[alembic/: DB Migrations]
        Alembic --> ProdDB[(PostgreSQL: Prod / Dev DB)]
    end

    %% Testing & CI/CD Infrastructure
    subgraph TestingInfra [Testing & CI/CD]
        CI[.github/workflows/: CI Pipeline] --> Pytest[tests/: Pytest, Mocks & Integration]
        Pytest --> TestDB[(PostgreSQL: weather_test_db)]
        CI --> Docker[Docker Compose Stack]
    end

    classDef db fill:#f9f,stroke:#333,stroke-width:1px;
    class ProdDB,TestDB db;
```
