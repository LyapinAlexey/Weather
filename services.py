import logging
import requests
from config import Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherService:
    @staticmethod
    def get_city_by_ip() -> str:
        try:
            response = requests.get(Config.IP_GEO_URL, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return data.get("city", "London")
        except requests.RequestException as e:
            logger.error(f"Failed to get city by IP: {e}")
        return "London"  # Default city
    @staticmethod
    def get_weather(city: str) -> dict:
        """Запрашивает сырые данные о погоде у провайдера WeatherAPI."""
        if not Config.WEATHER_API_KEY:
            return {"error": "API key is missing in environment variables (.env)."}
        params = {
            "key": Config.WEATHER_API_KEY,
            "q": city,
            "days": 3,
            "aqi": "yes",
            "alerts": "no",
            "lang": "en"
        }
        try:
            response = requests.get(Config.WEATHER_URL, params=params, timeout=5)
            
            # If code = 400 — incorrect city
            if response.status_code == 400:
                return {"error": f"City '{city}' not found."}
                
            # Another errors
            if response.status_code != 200:
                return {"error": "Weather service is temporary unavailable."}
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Network error while fetching weather for {city}: {e}")
            return {"error": "Network error. Please check your internet connection."}
