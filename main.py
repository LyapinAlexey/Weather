# --- If you in Russia, turn ON VPN ---
from datetime import datetime
import requests
import os
import sys
import platform
import subprocess
def get_weather():
    city = "Москва"
    lat = 55.675093
    lon = 37.550441
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,pressure_msl,precipitation_probability,uv_index&hourly=temperature_2m,precipitation_probability,uv_index,pressure_msl&timezone=auto"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except Exception as error:
        print(f"Ошибка при получении данных погоды: {error}")
        return
    now = datetime.now()
    print(f"Дата и время: {now.strftime('%d.%m.%Y %H:%M:%S')}")
    print("-" * 70)
    current_temp = data["current"]["temperature_2m"]
    current_uv = round(data["current"]["uv_index"])
    current_pha = round((data["current"]["pressure_msl"]) * 0.750062)
    current_rain = data["current"]["precipitation_probability"]
    print(f"Город: {city}")
    print(f"Текущая температура: {current_temp}°C")
    print(f"Текущий УФ-индекс: {current_uv}")
    print(f"Текущее давление: {current_pha}мм")
    print(f"Вероятность осадков: {current_rain}%")
    print("-" * 70)
    print("Прогноз на 24 часа:")
    print(f"{'Время':<8} | {'Температура':<8} | {'Вероятность осадков':<8} | {'УФ-индекс':<10} | {'Давление':<12}")
    print("-" * 70)
    hourly = data["hourly"]
    current_hour_str = now.strftime("%Y-%m-%dT%H:00")
    hours_printed = 0
    for i, time_str in enumerate(hourly["time"]):
        if time_str >= current_hour_str:
            display_time = time_str.split("T")[1]
            temp = hourly["temperature_2m"][i]
            rain_prob = hourly["precipitation_probability"][i]
            hpa = round((hourly["pressure_msl"][i]) * 0.750062)
            uv = round(hourly["uv_index"][i])
            print(f"{display_time:<8} | {f'{temp}°C':<11} | {f'{rain_prob}%':<19} | {f'{uv}':<10} | {f'{hpa} мм'}")
            hours_printed += 1
            if hours_printed == 24: break
if __name__ == "__main__":
    print("Нужно ли напечатать прогноз?(Используется стандартный принтер)\n0 - нет; 1 - да")
    way = input("Input way: ")
    print("-" * 70)
    if way == "1":
        filename = "weather_report.txt"
        original_stdout = sys.stdout
        current_os = platform.system()
        file_encoding = "utf-16" if current_os == "Windows" else "utf-8"
        with open(filename, "w", encoding=file_encoding) as f:
            sys.stdout = f
            get_weather()
        sys.stdout = original_stdout
        try:
            if current_os == "Windows":
                subprocess.run(f'notepad.exe /p "{filename}"', shell=True, check=True)
                print("Документ успешно отправлен на печать в Windows!")
            elif current_os in ["Linux", "Darwin"]:
                subprocess.run(["lp", filename], capture_output=True, text=True, check=True)
                print("Документ успешно отправлен в очередь печати UNIX!")
            else: print(f"Ошибка: Операционная система {current_os} не поддерживается для печати.")
        except Exception as e: print(f"Не удалось отправить на печать: {e}")
    else: get_weather()