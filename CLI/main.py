import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from datetime import datetime
import platform
import subprocess
from config import Config
from services import WeatherService
RESET, BOLD, BLUE, CYAN, GREEN, YELLOW, RED, ORANGE = (
    "\033[0m", "\033[1m", "\033[34m", "\033[36m", "\033[32m", "\033[33m", "\033[31m", "\033[35m"
)
class WeatherReport:
    def __init__(self, data: dict, for_printing: bool = False):
        self.data = data
        self.for_printing = for_printing
        self.loc, self.curr = data["location"], data["current"]
        self.line_len = 81 if for_printing else 70
    def _fmt(self, val, color) -> str:
        return str(val) if self.for_printing else f"{color}{val}{RESET}"
    def get_color_metrics(self):
        t, uv, p = self.curr["temp_c"], round(self.curr["uv"]), round(self.curr["pressure_mb"] * 0.750062)
        tc = BLUE if t < -10 else CYAN if t < 0 else GREEN if t < 16 else YELLOW if t < 26 else RED
        uc = GREEN if uv <= 2 else YELLOW if uv <= 5 else ORANGE if uv <= 7 else RED
        pc = CYAN if p < 745 else GREEN if p <= 755 else YELLOW if p <= 765 else RED
        return self._fmt(f"{t}°C", tc), self._fmt(uv, uc), self._fmt(f"{p} мм", pc)
    def display(self):
        print(f" Date and time: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n" + "-" * self.line_len)
        print(f" Город: {self.loc['name']} ({self.loc['country']})" if self.for_printing else f" City: {BOLD}{self.loc['name']}{RESET} ({BOLD}{self.loc['country']}{RESET})")
        t_out, uv_out, p_out = self.get_color_metrics()
        print(f" Current temperature: {t_out}\n Current UV index: {uv_out}\n Current pressure: {p_out}\n Weather: {self.curr['condition']['text']}\n" + "-" * self.line_len)
        print(" Forecast for 24 hours:\n" + f"{' Time':<7} | {'Temperature':<8} | {'UV Index':<9} | {'Pressure':<12}\n" + "-" * self.line_len)
        local_hr = datetime.strptime(self.loc["localtime"], "%Y-%m-%d %H:%M").strftime("%Y-%m-%d %H:00")
        hours = [h for day in self.data["forecast"]["forecastday"] for h in day["hour"] if h["time"] >= local_hr][:24]
        for h in hours:
            print(f" {h['time'].split(' ')[1]:<6} | {f'{h['temp_c']}°C':<11} | {round(h['uv']):<9} | {f'{round(h['pressure_mb'] * 0.750062)} мм':<12}")
        print("-" * self.line_len)
class Main:
    def run(self):
        srv = WeatherService()
        city = srv.get_city_by_ip()
        print(f"📍 Location context: {city}")
        data = srv.get_weather(city)
        if "error" in data:
            return print(f"⚠️ {data['error']}")
        print_req = input("Need to print the forecast? (No; Yes): ").strip().lower() == "yes"
        print("-" * 70)
        report = WeatherReport(data, for_printing=print_req)
        if not print_req:
            return report.display()
        fn, os_t = "CLI/weather_report.txt", platform.system()
        orig = sys.stdout
        with open(fn, "w", encoding="utf-8-sig" if os_t == "Windows" else "utf-8") as f:
            sys.stdout = f
            report.display()
        sys.stdout = orig
        try:
            subprocess.run(f'notepad.exe /p "{fn}"' if os_t == "Windows" else ["lp", fn], shell=(os_t == "Windows"), check=True)
            print("✅ Document successfully printed!")
        except Exception as e:
            print(f"⚠️ Print spooler failed: {e}")
if __name__ == "__main__":
    Main().run()