from datetime import datetime
import requests
import sys
import os
import platform
import subprocess
RESET = "\033[0m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
ORANGE = "\033[35m"
RED = "\033[31m"
BLUE = "\033[34m"
CYAN = "\033[36m"
BOLD = "\033[1m"
for_printing = False
API_KEY = os.getenv("WEATHER_API_KEY")
KEY_FILE = "CLI/weather_key.txt"
if not API_KEY and os.path.exists(KEY_FILE):
    with open(KEY_FILE, "r", encoding="utf-8") as f: API_KEY = f.read().strip()
if not API_KEY:
    print("🔑 API-key not found.")
    API_KEY = input("Please insert your WeatherAPI Key: ").strip()
    try:
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            f.write(API_KEY)
        print(f"✅ Key successfully saved to file '{KEY_FILE}' and will not be required again!")
        print("-" * 70)
    except Exception as e:
        print(f"⚠️ Failed to save key to file: {e}")
def get_weather(for_printing):
    try:
        response_ip = requests.get("http://ip-api.com/json/").json()
        if response_ip.get("status") == "success":
            city = response_ip.get("city", "Unknown city")
            lat = response_ip.get("lat")
            lon = response_ip.get("lon")
        else:
            print("⚠️Error: Geolocation service returned failure status.")
            return
    except Exception as err:
        print(f"⚠️Error occurred while determining location via API: {err}")
        return
    city_query = city
    try: url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city_query}&days=3&aqi=yes&alerts=no&lang=ru"
    except Exception as er:
        print(f"⚠️Error occurred while forming URL: {er}")
        return
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as error:
        print(f"⚠️Error occurred while fetching weather data: {error}")
        return
    now = datetime.now()
    print(f" Date and time: {now.strftime('%d.%m.%Y %H:%M:%S')}")
    if for_printing: print("-" * 81)
    else: print("-" * 70)
    location = data["location"]
    api_local_time = datetime.strptime(location["localtime"], "%Y-%m-%d %H:%M")
    forecast_day = data["forecast"]["forecastday"]
    current_hour_int = api_local_time.hour
    current_temp = data["current"]["temp_c"]
    current_uv = round(data["current"]["uv"])
    current_pha = round(data["current"]["pressure_mb"] * 0.750062) 
    current_condition = data["current"]["condition"]["text"]
    aqi_data = data["current"].get("air_quality", {})
    epa_index = aqi_data.get("us-epa-index", 0)
    try: current_rain = forecast_day[0]["hour"][current_hour_int]["chance_of_rain"]
    except (IndexError, KeyError): current_rain = None
    aqi_status = ("No data", RESET)
    uv_status = ("No data", RESET)
    temp_status = ("No data", RESET)
    pha_status = ("No data", RESET)
    rain_status = ("No data", RESET)
    if epa_index == 1: aqi_status = ("Excellent (Clean air)", GREEN)
    elif epa_index == 2: aqi_status = ("Moderate (Normal)", YELLOW)
    elif epa_index == 3: aqi_status = ("Low (Harmful for sensitive groups)", ORANGE)
    elif epa_index == 4: aqi_status = ("High (Negative impact)", ORANGE)
    elif epa_index == 5: aqi_status = ("Very high (Dangerous for health)", RED)
    elif epa_index == 6: aqi_status = ("Hazardous (Emergency situation)", RED)
    aqi_text, aqi_color = aqi_status
    if 0 <= current_uv <= 2: uv_status = (str(current_uv), GREEN)
    elif 3 <= current_uv <= 5: uv_status = (str(current_uv), YELLOW)
    elif 6 <= current_uv <= 7: uv_status = (str(current_uv), ORANGE)
    elif current_uv >= 8: uv_status = (str(current_uv), RED)
    uv_text, uv_color = uv_status
    if current_temp < -10.0: temp_status = (f"{current_temp}°C", BLUE)
    elif -10.0 <= current_temp < 0.0: temp_status = (f"{current_temp}°C", CYAN)
    elif 0.0 <= current_temp < 16.0: temp_status = (f"{current_temp}°C", GREEN)
    elif 16.0 <= current_temp < 26.0: temp_status = (f"{current_temp}°C", YELLOW)
    elif current_temp >= 26.0: temp_status = (f"{current_temp}°C", RED)
    temp_text, temp_color = temp_status
    if current_pha < 745: pha_status = (f"{current_pha} мм (Low)", CYAN)   
    elif 745 <= current_pha <= 755: pha_status = (f"{current_pha} мм (Good)", GREEN)
    elif 756 <= current_pha <= 765: pha_status = (f"{current_pha} мм (Normal)", YELLOW)
    elif current_pha >= 766: pha_status = (f"{current_pha} мм (High)", RED)
    pha_text, pha_color = pha_status
    if current_rain < 30: rain_status = (f"{current_rain}%", RESET)   
    elif 31 <= current_rain < 60: rain_status = (f"{current_rain}%", CYAN)
    elif current_rain >= 61: rain_status = (f"{current_rain}%", BLUE)    
    rain_text, rain_color = rain_status
    loc = f" City: {BOLD}{location['name']}{RESET} ({BOLD}{location['country']}{RESET})"  
    if for_printing:
        aqi_display = aqi_text
        uv_display = uv_text
        temp_display = temp_text
        pha_display = pha_text
        rain_display = rain_text
        loc = f" Город: {location['name']} ({location['country']})"  
    else:
        aqi_display = f"{aqi_color}{aqi_text}{RESET}"
        uv_display = f"{uv_color}{uv_text}{RESET}"
        temp_display = f"{temp_color}{temp_text}{RESET}"
        pha_display = f"{pha_color}{pha_text}{RESET}"
        rain_display = f"{rain_color}{rain_text}{RESET}"
    print(loc)
    print(f" Current temperature: {temp_display}")
    print(f" Air quality: {aqi_display}")
    print(f" Current UV index: {uv_display}")
    print(f" Current pressure: {pha_display}")
    print(f" Probability of precipitation: {rain_display}")
    print(f" Weather: {current_condition}")
    if for_printing: print("-" * 81)
    else: print("-" * 70)
    print(" Forecast for 24 hours:")
    print(f"{' Time':<7} | {'Temperature':<8} | {'Precipitation':<8} | {'UV Index':<9} | {'Pressure':<12}")
    if for_printing: print("-" * 81)
    else: print("-" * 70)
    all_hours = []
    for day in forecast_day: all_hours.extend(day["hour"])
    current_hour_str = api_local_time.strftime("%Y-%m-%d %H:00")
    hours_printed = 0
    for hour in all_hours:
        if hour["time"] >= current_hour_str:
            display_time = hour["time"].split(" ")[1]
            temp = hour["temp_c"]
            rain_prob = hour["chance_of_rain"]
            hpa = round(hour["pressure_mb"] * 0.750062)
            uv = round(hour["uv"])
            condition_text = hour["condition"]["text"]
            print(f" {display_time:<6} | {f'{temp}°C':<11} | {f'{rain_prob}%':<19} | {f'{uv}':<9} | {f'{hpa} мм':<12}")
            hours_printed += 1
            if hours_printed == 24: break
    if for_printing:
        print("-" * 81)
        print(" Forecast for 3 days:")
        print(f"{' Date':<11} | {'Avg. Temp':<11} | {'Precipitation':<9} | {'Max UV':<7} | {'Wind Speed':<14} | {'Gusts':<12}")
        for day in data["forecast"]["forecastday"]:
            date_obj = datetime.strptime(day["date"], "%Y-%m-%d")
            parsed_date = date_obj.strftime("%d.%m.%Y")
            t_mean = day["day"]["avgtemp_c"]
            rain_sum = day["day"]["totalprecip_mm"]
            uv_max = round(day["day"]["uv"])
            wind_max = day["day"]["maxwind_kph"]
            gusts_max = round(wind_max * 1.2) 
            print(f" {parsed_date:<9} | {f'{t_mean}°C':<11} | {f'{rain_sum} мм':<9} | {f'{uv_max}':<7} | {f'{wind_max} км/ч':<14} | {f'{gusts_max} км/ч':<12}")
    if for_printing: print("-" * 81) 
    else: print("-" * 70)
if __name__ == "__main__":
    print("Need to print the forecast?(Using default printer)")
    way = input("No; Yes: ")
    print("-" * 70)
    if way.lower() == "yes":
        for_printing = True
        filename = "weather_report.txt"
        original_stdout = sys.stdout
        current_os = platform.system()
        file_encoding = "utf-8-sig" if current_os == "Windows" else "utf-8"
        try:
            with open(filename, "w", encoding=file_encoding) as f:
                sys.stdout = f
                get_weather(for_printing)
        finally: sys.stdout = original_stdout
        try:
            if current_os == "Windows":
                subprocess.run(f'notepad.exe /p "{filename}"', shell=True, check=True)
                print("✅Document successfully sent to print in Windows!")
            elif current_os in ["Linux", "Darwin"]:
                subprocess.run(["lp", filename], capture_output=True, text=True, check=True)
                print("✅Document successfully sent to print queue in UNIX!")
            else: print(f"⚠️Error: Operating system {current_os} is not supported for printing.")
        except Exception as e: print(f"⚠️Failed to send to print: {e}")
    else:
        for_printing = False
        get_weather(for_printing)