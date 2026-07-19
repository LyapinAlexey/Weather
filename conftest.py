import pytest
import os
from WEB import app as flask_app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import WeatherRequest

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL)
    connection = engine.connect()
    transaction = connection.begin()
    TestSessionLocal = sessionmaker(bind=connection)
    session = TestSessionLocal()
    yield session
    session.close()
    transaction.rollback()
    connection.close()
@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client
@pytest.fixture
def fake_weather_response() -> dict:
    return {
        "location": {
            "localtime": "2026-07-16 12:00",
                "name": "Berlin",
                "country": "Germany",
                },
        "current": {
            "temp_c": 20,
            "condition": {"text": "Sunny"},
            "uv": 5,
            "pressure_mb": 760,
        },
        "forecast": {
            "forecastday": [
                {
                    "date": "2026-07-16",
                    "day": {
                        "avgtemp_c": 22,
                        "totalprecip_mm": 0,
                        "uv": 5,
                        "maxwind_kph": 10,
                        "gust_kph": 15,
                    },
                    "hour": [
                        {
                            "time": "2026-07-16 12:00",
                            "temp_c": 20,
                            "chance_of_rain": 0,
                            "chance_of_snow": 0,
                            "uv": 5,
                            "pressure_mb": 1013
                        }
                    ]
                }
            ]
        }
    }