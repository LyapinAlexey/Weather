# --- If you in Russia, turn ON VPN ---
from datetime import datetime
import requests
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
    current_uv = data["current"]["uv_index"]
    current_pha = round((data["current"]["pressure_msl"]) * 0.750062)
    current_rain = data["current"]["precipitation_probability"]
    print(f"Город: {city}")
    print(f"Текущая температура: {current_temp}°C")
    print(f"Текущий УФ-индекс: {current_uv}")
    print(f"Текущее давление: {current_pha}мм")
    print(f"Вероятность осадков: {current_rain}%")
    print("-" * 70)
    print("Прогноз на оставшуюся часть дня:")
    print(f"{'Время':<8} | {'Температура':<8} | {'Вероятность осадков':<8} | {'УФ-индекс':<10} | {'Давление':<12}")
    print("-" * 70)
    hourly = data["hourly"]
    current_hour_str = now.strftime("%Y-%m-%dT%H:00")
    for i, time_str in enumerate(hourly["time"]):
        if (time_str >= current_hour_str and time_str.split("T")[0] == now.strftime("%Y-%m-%d")):
            display_time = time_str.split("T")[1]
            temp = hourly["temperature_2m"][i]
            rain_prob = hourly["precipitation_probability"][i]
            hpa = round((hourly["pressure_msl"][i]) * 0.750062)
            uv = hourly["uv_index"][i]
            print(f"{display_time:<8} | {f'{temp}°C':<11} | {f'{rain_prob}%':<19} | {f'{uv}':<10} | {f'{hpa} мм'}")
if __name__ == "__main__":
    get_weather()