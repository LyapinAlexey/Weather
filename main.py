# --- If you in Russia, turn ON VPN ---
from datetime import datetime
import requests
import sys
import platform
import subprocess
import geocoder
for_printing = False
API_KEY = "0f9495745ad44d309e5155406262406" 
def get_weather(for_printing):
    try:
        response_ip = requests.get("http://ip-api.com/json/").json()
        if response_ip.get("status") == "success":
            city = response_ip.get("city", "Неизвестный город")
            lat = response_ip.get("lat")
            lon = response_ip.get("lon")
        else:
            print("Ошибка: Сервис геолокации вернул неудачный статус.")
            return
    except Exception as err:
        print(f"Ошибка при определении локации через API: {err}")
        return
    city_query = city
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={city_query}&days=7&aqi=no&alerts=no&lang=ru"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as error:
        print(f"Ошибка при получении данных погоды: {error}")
        return
    now = datetime.now()
    print(f" Дата и время: {now.strftime('%d.%m.%Y %H:%M:%S')}")
    if for_printing: print("-" * 81)
    else: print("-" * 70)
    location = data["location"]
    forecast_day = data["forecast"]["forecastday"]
    current_hour_int = now.hour
    current_temp = data["current"]["temp_c"]
    current_uv = round(data["current"]["uv"])
    current_pha = round(data["current"]["pressure_mb"] * 0.750062) 
    current_condition = data["current"]["condition"]["text"]
    try: current_rain = forecast_day[0]["hour"][current_hour_int]["chance_of_rain"]
    except (IndexError, KeyError): current_rain = None
    print(f" Город: {location['name']} ({location['country']})")
    print(f" Текущая температура: {current_temp}°C")
    print(f" Состояние: {current_condition}")
    print(f" Текущий УФ-индекс: {current_uv}")
    print(f" Текущее давление: {current_pha} мм рт. ст.")
    print(f" Вероятность осадков: {current_rain}%")
    print(f" Погода: {current_condition}")
    if for_printing: print("-" * 81)
    else: print("-" * 70)
    print(" Прогноз на 24 часа:")
    print(f"{' Время':<7} | {'Температура':<8} | {'Вероятность осадков':<8} | {'УФ-индекс':<10} | {'Давление':<12}")
    if for_printing: print("-" * 81)
    else: print("-" * 70)
    all_hours = []
    for day in forecast_day: all_hours.extend(day["hour"])
    current_hour_str = now.strftime("%Y-%m-%d %H:00")
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
        print(" Прогноз на неделю:")
        print(f"{' Дата':<11} | {'Сред. темп.':<11} | {'Осадки':<9} | {'Макс.УФ':<7} | {'Скорость ветра':<14} | {'Порыв ветра':<12}")
        print("-" * 81)
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
    print("Нужно ли напечатать прогноз?(Используется стандартный принтер)")
    way = input("0 - нет; 1 - да: ")
    print("-" * 70)
    if way == "1":
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
                print("Документ успешно отправлен на печать в Windows!")
            elif current_os in ["Linux", "Darwin"]:
                subprocess.run(["lp", filename], capture_output=True, text=True, check=True)
                print("Документ успешно отправлен в очередь печати UNIX!")
            else: print(f"Ошибка: Операционная система {current_os} не поддерживается для печати.")
        except Exception as e: print(f"Не удалось отправить на печать: {e}")
    else:
        for_printing = False
        get_weather(for_printing)