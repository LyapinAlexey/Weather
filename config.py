import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    WEATHER_URL = "https://api.weatherapi.com/v1/forecast.json"
    IP_GEO_URL = "https://ip-api.com"
    SECRET_KEY = os.getenv("SECRET_KEY", "default-fallback-key")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
