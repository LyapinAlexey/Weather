import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for
from config import Config
from services import WeatherService
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = getattr(Config, "SECRET_KEY", "super-secret-weather-key")
def determine_bg_class(condition_text: str) -> str:
    text = condition_text.lower()
    if any(word in text for word in ["clear", "sunny"]):
        return "sunny"
    if "rain" in text:
        return "rainy"
    if "cloud" in text:
        return "cloudy"
    if "thunder" in text:
        return "thunder"
    return "sunny"
@app.route("/", methods=["GET", "POST"])
def index():
    config_api_key = getattr(Config, "WEATHER_API_KEY", None)

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        user_api_key = request.form.get("api_key", "").strip()
        if user_api_key:
            session["api_key"] = user_api_key
            return redirect(url_for("index"))
    else:
        city = None
    active_api_key = config_api_key or session.get("api_key")
    if not active_api_key:
        return render_template(
            "index.html",
            error="API key is missing. Please enter your WeatherAPI key below.",
            bg_class="sunny",
            now=datetime.now().strftime('%Y-%m-%d %H:%M'),
            needs_key=True
        )
    if not city:
        city = WeatherService.get_city_by_ip() 
        if not city:
            city = "Moscow" 
    data = WeatherService.get_weather(city, api_key=active_api_key)
    if "error" in data:
        if not config_api_key and "api_key" in session:
            session.pop("api_key", None)
        return render_template(
            "index.html", 
            error=data["error"].get("message", "Invalid API Key or City not found."), 
            bg_class="sunny", 
            now=datetime.now().strftime('%Y-%m-%d %H:%M'),
            needs_key=not config_api_key
        )
    hourly_forecast = []
    api_localtime = datetime.strptime(data["location"]["localtime"], "%Y-%m-%d %H:%M")
    current_hour_str = api_localtime.strftime("%Y-%m-%d %H:00")
    all_hours = [hour for day in data["forecast"]["forecastday"] for hour in day["hour"]]
    count = 0
    for hour in all_hours:
        if hour["time"] >= current_hour_str:
            prob_precip = max(hour.get("chance_of_rain", 0), hour.get("chance_of_snow", 0))
            
            hourly_forecast.append({
                "time": hour["time"].split(" ")[1],
                "temp": hour["temp_c"],
                "precipitation": prob_precip,
                "uv": round(hour["uv"]),
                "pressure": round(hour["pressure_mb"] * 0.750062) 
            })
            count += 1
            if count == 24:
                break
    daily_forecast = []
    for day in data["forecast"]["forecastday"]:
        d_obj = datetime.strptime(day["date"], "%Y-%m-%d")
        daily_forecast.append({
            "date": d_obj.strftime("%d.%m.%Y"),
            "temp": day["day"]["avgtemp_c"],
            "precipitation": day["day"]["totalprecip_mm"],
            "uv": round(day["day"]["uv"]),
            "wind": day["day"]["maxwind_kph"],
            "gust": round(day["day"].get("gust_kph", day["day"]["maxwind_kph"] * 1.2))
        })
    bg_class = determine_bg_class(data["current"]["condition"]["text"])
    return render_template(
        "index.html",
        weather=data,
        hourly=hourly_forecast,
        daily=daily_forecast,
        bg_class=bg_class,
        now=datetime.now().strftime('%Y-%m-%d %H:%M'),
        show_key_input=not config_api_key
    )
if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5001))
    app.run(host="0.0.0.0", port=port)

