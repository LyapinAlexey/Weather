import logging
import requests
from config import Config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherService:
    @staticmethod
    def get_city_by_ip() -> str:
        try:
            response = requests.get(Config.IP_GEO_URL, timeout=3)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    return data.get("city", "Moscow")
        except Exception as e:
            logger.error(f"IP-Geo Error: {e}")
        try:
            ip_resp = requests.get("https://ipify.org", timeout=2)
            if ip_resp.status_code == 200:
                ip = ip_resp.json().get("ip")
                geo_resp = requests.get(f"http://ip-api.com{ip}", timeout=2)
                if geo_resp.status_code == 200 and geo_resp.json().get("status") == "success":
                    return geo_resp.json().get("city")
        except Exception:
            pass
        try:
            response = requests.get("https://ipinfo.io", timeout=2)
            if response.status_code == 200:
                return response.json().get("city")
        except Exception:
            pass
        return "Moscow"  # Fallback city if all else fails
    @staticmethod
    def get_weather(city: str) -> dict:
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
            if response.status_code == 400:
                return {"error": f"City '{city}' not found."}
            if "application/json" not in response.headers.get("Content-Type", ""):
                return {
                    "error": f"API returned invalid response format (Status: {response.status_code}). "
                             f"Perhaps access is blocked. Please enable or change your VPN location!"
                }
            if response.status_code != 200:
                return {"error": f"Weather service error. Status code: {response.status_code}"}
            try:
                return response.json()
            except ValueError:
                return {"error": "Error parsing response from server. Please check your internet connection."}
                
        except requests.RequestException as e:
            logger.error(f"Network error while fetching weather for {city}: {e}")
            return {"error": "Network error. Look up your internet connection or try again later."}

