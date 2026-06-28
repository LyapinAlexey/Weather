from flask import Flask, render_template, request
from datetime import datetime
import requests
import os
app = Flask(__name__)
KEY_FILE = "weather_key.txt"
API_KEY = None
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "r", encoding="utf-8") as f:
        API_KEY = f.read().strip()
def get_weather_data(city):
    if not API_KEY:
        return {"error": "🔑 API key not found in weather_key.txt!"}
    try:
        url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city}&days=3&aqi=yes&alerts=no&lang=en"
        response = requests.get(url)
        if response.status_code != 200:
            return {"error": f"City '{city}' not found or API error."}
        return response.json()
    except Exception as e:
        return {"error": f"Network error: {e}"}
@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    hourly_forecast = []
    daily_forecast = []
    error_msg = None
    bg_class = "default"  
    city = "London"
    try:
        ip_res = requests.get("http://ip-api.com/json/").json()
        if ip_res.get("status") == "success":
            city = ip_res.get("city", "London")
    except: pass
    if request.method == "POST":
        city = request.form.get("city")
    data = get_weather_data(city)
    if "error" in data:
        error_msg = data["error"]
    else:
        weather_data = data
        condition = data["current"]["condition"]["text"].lower()
        bg_class = "sunny"
        if "clear" in condition or "sunny" in condition:
            bg_class = "sunny"
        elif "rain" in condition:
            bg_class = "rainy"
        elif "cloud" in condition:
            bg_class = "cloudy"
        api_local_time = datetime.strptime(data["location"]["localtime"], "%Y-%m-%d %H:%M")
        current_hour_str = api_local_time.strftime("%Y-%m-%d %H:00")
        all_hours = []
        for day in data["forecast"]["forecastday"]:
            all_hours.extend(day["hour"])  
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
                if count == 24: break
        for day in data["forecast"]["forecastday"]:
            d_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            daily_forecast.append({
                "date": d_obj.strftime("%d.%m.%Y"),
                "temp": day["day"]["avgtemp_c"],
                "precipitation": day["day"]["totalprecip_mm"],
                "uv": round(day["day"]["uv"]),
                "wind": day["day"]["maxwind_kph"],
                "gust": round(day["day"].get("maxwind_kph", 0))
            })
    return render_template(
        "index.html", 
        weather=weather_data, 
        hourly=hourly_forecast, 
        daily=daily_forecast, 
        error=error_msg, 
        bg_class=bg_class, 
        now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
if __name__ == "__main__":
    app.run(debug=True, port=5001)