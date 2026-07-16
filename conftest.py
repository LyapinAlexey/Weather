import pytest
from WEB import app as flask_app

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