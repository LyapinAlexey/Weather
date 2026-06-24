# --- If you in Russia, turn ON VPN ---
from datetime import datetime
import requests
import sys
import platform
import subprocess
for_printing = False
def get_weather(for_printing):
    city = "Москва"
    lat = 55.675093
    lon = 37.550441
    url = (f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
    f"&current=temperature_2m,pressure_msl,precipitation_probability,uv_index"
    f"&hourly=temperature_2m,precipitation_probability,uv_index,pressure_msl"
    f"&daily=temperature_2m_mean,precipitation_sum,uv_index_max,wind_speed_10m_max,wind_gusts_10m_max"
    f"&timezone=auto")
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
    current_temp = data["current"]["temperature_2m"]
    current_uv = round(data["current"]["uv_index"])
    current_pha = round((data["current"]["pressure_msl"]) * 0.750062)
    current_rain = data["current"]["precipitation_probability"]
    print(f" Город: {city}")
    print(f" Текущая температура: {current_temp}°C")
    print(f" Текущий УФ-индекс: {current_uv}")
    print(f" Текущее давление: {current_pha}мм")
    print(f" Вероятность осадков: {current_rain}%")
    if for_printing: print("-" * 81)
    else: print("-" * 70)
    print(" Прогноз на 24 часа:")
    print(f"{' Время':<8} | {'Температура':<8} | {'Вероятность осадков':<8} | {'УФ-индекс':<10} | {'Давление':<12}")
    if for_printing: print("-" * 81)
    else: print("-" * 70)
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
            print(f" {display_time:<7} | {f'{temp}°C':<11} | {f'{rain_prob}%':<19} | {f'{uv}':<10} | {f'{hpa} мм'}")
            hours_printed += 1
            if hours_printed == 24: break
    if for_printing:
        print("-" * 81)
        print(" Прогноз на неделю:")
        print(f"{' Дата':<11} | {'Сред. темп.':<12} | {'Осадки':<10} | {'Макс. УФ':<8} | {'Скорость ветра':<15} | {'Порыв ветра':<14}")
        print("-" * 81)
        daily = data["daily"]
        for i, date_str in enumerate(daily["time"]):
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d.%m.%Y")
            t_mean = daily["temperature_2m_mean"][i]
            rain_sum = daily["precipitation_sum"][i]
            uv_max = round(daily["uv_index_max"][i])
            wind_max = daily["wind_speed_10m_max"][i]
            gusts_max = daily["wind_gusts_10m_max"][i]
            print(f" {parsed_date:<10} | {f'{t_mean}°C':<12} | {f'{rain_sum} мм':<10} | {f'{uv_max}':<8} | {f'{wind_max} км/ч':<15} | {f'{gusts_max} км/ч':<9}")
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
        file_encoding = "cp1251" if current_os == "Windows" else "utf-8"
        try:
            with open(filename, "w", encoding=file_encoding) as f:
                sys.stdout = f
                get_weather(for_printing)
        finally: sys.stdout = original_stdout
        try:
            if current_os == "Windows":
                # subprocess.run(f'notepad.exe /p "{filename}"', shell=True, check=True)
                print("Документ успешно отправлен на печать в Windows!")
            elif current_os in ["Linux", "Darwin"]:
                # subprocess.run(["lp", filename], capture_output=True, text=True, check=True)
                print("Документ успешно отправлен в очередь печати UNIX!")
            else: print(f"Ошибка: Операционная система {current_os} не поддерживается для печати.")
        except Exception as e: print(f"Не удалось отправить на печать: {e}")
    else:
        for_printing = False
        get_weather(for_printing)