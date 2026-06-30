from datetime import datetime
import os
import platform
import subprocess
import sys
import requests
# Terminal colors
RESET, GREEN, YELLOW, ORANGE, RED, BLUE, CYAN, BOLD = (
    "\033[0m", "\033[32m", "\033[33m", "\033[35m", "\033[31m", "\033[34m", "\033[36m", "\033[1m"
)
class WeatherService:
    def __init__(self):
        self.api_key = self._load_key()
    def _load_key(self):
        #Finds or asks for the API key.
        key_file = "CLI/weather_key.txt"
        key = os.getenv("WEATHER_API_KEY")
        if not key and os.path.exists(key_file):
            with open(key_file, "r", encoding="utf-8") as f:
                key = f.read().strip()
        if not key:
            key = input("🔑 Please insert your WeatherAPI Key: ").strip()
            os.makedirs("CLI", exist_ok=True)
            with open(key_file, "w", encoding="utf-8") as f:
                f.write(key)
        return key
    def get_city_by_ip(self):
        try:
            res = requests.get("http://ip-api.com/json/").json()
            return res.get("city") if res.get("status") == "success" else None
        except Exception:
            return None
    def fetch_forecast(self, city):
        url = f"http://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={city}&days=3&aqi=yes&alerts=no&lang=en"
        try:
            res = requests.get(url)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            print(f"⚠️ Error fetching weather: {e}")
            return None
class WeatherReport:
    #Handles color calculations and building the text output.
    def __init__(self, data, for_printing=False):
        self.data = data
        self.for_printing = for_printing
        self.loc = data["location"]
        self.curr = data["current"]
        self.days = data["forecast"]["forecastday"]
        self.local_time = datetime.strptime(self.loc["localtime"], "%Y-%m-%d %H:%M")
        self.line_len = 81 if for_printing else 70
    def _color(self, text, color_code):
        #Applies color only if we are NOT printing to physical paper.
        return text if self.for_printing else f"{color_code}{text}{RESET}"
    def get_metrics(self):
        temp = self.curr["temp_c"]
        t_color = BLUE if temp < -10 else CYAN if temp < 0 else GREEN if temp < 16 else YELLOW if temp < 26 else RED
        uv = round(self.curr["uv"])
        uv_color = GREEN if uv <= 2 else YELLOW if uv <= 5 else ORANGE if uv <= 7 else RED
        pha = round(self.curr["pressure_mb"] * 0.750062)
        p_color = CYAN if pha < 745 else GREEN if pha <= 755 else YELLOW if pha <= 765 else RED
        return (
            self._color(f"{temp}°C", t_color),
            self._color(str(uv), uv_color),
            self._color(f"{pha} мм", p_color)
        )
    def print_all(self):
        print(f" Date and time: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
        print("-" * self.line_len)
        if self.for_printing:
            print(f" Город: {self.loc['name']} ({self.loc['country']})")
        else:
            print(f" City: {BOLD}{self.loc['name']}{RESET} ({BOLD}{self.loc['country']}{RESET})")
        temp_out, uv_out, pha_out = self.get_metrics()
        print(f" Current temperature: {temp_out}")
        print(f" Current UV index: {uv_out}")
        print(f" Current pressure: {pha_out}")
        print(f" Weather: {self.curr['condition']['text']}")
        print("-" * self.line_len)
        print(" Forecast for 24 hours:")
        print(f"{' Time':<7} | {'Temperature':<8} | {'UV Index':<9} | {'Pressure':<12}")
        print("-" * self.line_len)
        all_hours = [hr for day in self.days for hr in day["hour"]]
        curr_str = self.local_time.strftime("%Y-%m-%d %H:00")
        count = 0
        for hr in all_hours:
            if hr["time"] >= curr_str:
                display_time = hr["time"].split(" ")[1]
                p_mm = round(hr["pressure_mb"] * 0.750062)
                print(f" {display_time:<6} | {f'{hr['temp_c']}°C':<11} | {f'{round(hr['uv'])}':<9} | {f'{p_mm} мм':<12}")
                count += 1
                if count == 24: break
        print("-" * self.line_len)
class App:
    #The main engine that controls the user flow.
    def __init__(self):
        self.service = WeatherService()
    def send_to_printer(self, report):
        filename = "weather_report.txt"
        os_type = platform.system()
        encoding = "utf-8-sig" if os_type == "Windows" else "utf-8"
        orig_stdout = sys.stdout
        with open(filename, "w", encoding=encoding) as f:
            sys.stdout = f
            report.print_all()
        sys.stdout = orig_stdout
        try:
            if os_type == "Windows":
                subprocess.run(f'notepad.exe /p "{filename}"', shell=True, check=True)
            elif os_type in ["Linux", "Darwin"]:
                subprocess.run(["lp", filename], check=True)
            print("✅ Document successfully sent to printer!")
        except Exception as e:
            print(f"⚠️ Printing failed: {e}")
    def run(self):
        city = self.service.get_city_by_ip()
        if not city:
            print("⚠️ Could not determine location.")
            return
        data = self.service.fetch_forecast(city)
        if not data: return
        choice = input("Need to print the forecast? (No; Yes): ").strip().lower()
        print("-" * 70)
        if choice == "yes":
            report = WeatherReport(data, for_printing=True)
            self.send_to_printer(report)
        else:
            report = WeatherReport(data, for_printing=False)
            report.print_all()
if __name__ == "__main__":
    App().run()