import copy
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from weatherender.CLI.main import Main, WeatherReport, print_file


class TestCLI:
    @pytest.fixture(autouse=True)
    def mock_dependencies(self):
        with (
            patch("weatherender.CLI.main.Config.validate"),
            patch("weatherender.CLI.main.SessionLocal") as mock_session_cls,
        ):
            mock_db = MagicMock()
            mock_session_cls.return_value = mock_db
            yield mock_db

    @pytest.fixture
    def prepared_weather_response(self, fake_weather_response):
        data = copy.deepcopy(fake_weather_response)
        data.setdefault("current", {})
        data["current"].setdefault("condition", {"text": "Sunny"})

        if "forecast" in data and "forecastday" in data["forecast"]:
            for fday in data["forecast"]["forecastday"]:
                day_dict = fday.setdefault("day", {})
                day_dict.setdefault("avgtemp_c", 15.0)
                day_dict.setdefault("mintemp_c", 10.0)
                day_dict.setdefault("maxtemp_c", 20.0)
                day_dict.setdefault("daily_chance_of_rain", 0)
                day_dict.setdefault("maxwind_kph", 10.0)
                day_dict.setdefault("uv", 3.0)
                day_dict.setdefault("totalprecip_mm", 0.0)
                day_dict.setdefault("condition", {"text": "Sunny"})
        return data

    @patch("weatherender.CLI.main.get_snow_state", return_value={"status": "No snow"})
    def test_weather_report_display(self, mock_snow, prepared_weather_response, capsys):
        report = WeatherReport(prepared_weather_response, for_printing=False)
        report.display()
        captured = capsys.readouterr()

        city_name = prepared_weather_response.get("location", {}).get("name", "Berlin")
        assert city_name in captured.out

    @patch("weatherender.CLI.main.get_snow_state", return_value={"status": "No snow"})
    def test_weather_report_for_printing(
        self, mock_snow, prepared_weather_response, capsys
    ):
        report = WeatherReport(prepared_weather_response, for_printing=True)
        report.display()
        captured = capsys.readouterr()

        city_name = prepared_weather_response.get("location", {}).get("name", "Berlin")
        assert city_name in captured.out
        assert "\033[1mNo snow\033[0m" not in captured.out

    @patch("weatherender.CLI.main.get_snow_state", return_value={"status": "No snow"})
    @patch("weatherender.CLI.main.WeatherService")
    def test_main_run_success_no_print(
        self,
        mock_service_cls,
        mock_snow,
        mock_dependencies,
        prepared_weather_response,
        monkeypatch,
        capsys,
    ):
        mock_service = MagicMock()
        mock_service.get_city_by_ip.return_value = "Moscow"
        mock_service.get_weather.return_value = prepared_weather_response
        mock_service_cls.return_value = mock_service

        monkeypatch.setattr("builtins.input", lambda _: "no")

        Main().run()

        captured = capsys.readouterr()
        assert "[+] Location context: Moscow" in captured.out
        assert mock_dependencies.add.called
        assert mock_dependencies.commit.called

    @patch("weatherender.CLI.main.get_snow_state", return_value={"status": "No snow"})
    @patch("weatherender.CLI.main.subprocess.run")
    @patch("weatherender.CLI.main.WeatherService")
    def test_main_run_success_with_print(
        self,
        mock_service_cls,
        mock_subproc,
        mock_snow,
        prepared_weather_response,
        monkeypatch,
        capsys,
        tmp_path,
    ):
        mock_service = MagicMock()
        mock_service.get_city_by_ip.return_value = "Moscow"
        mock_service.get_weather.return_value = prepared_weather_response
        mock_service_cls.return_value = mock_service

        monkeypatch.setattr("builtins.input", lambda _: "yes")
        report_file = tmp_path / "weather_report.txt"
        monkeypatch.setattr(
            "weatherender.CLI.main.Path",
            lambda *args, **kwargs: (
                report_file if "weather_report" in str(args) else Path(*args, **kwargs)
            ),
        )

        Main().run()

        captured = capsys.readouterr()

        assert "[+] Report saved to:" in captured.out
        assert report_file.exists() or "[+] Report saved to:" in captured.out

        assert (
            "[+] Sent to printer" in captured.out
            or "[!] File saved. Open it manually and print:" in captured.out
            or mock_subproc.called
        )

    @patch("weatherender.CLI.main.WeatherService")
    def test_main_run_error_handling(self, mock_service_cls, capsys):
        mock_service = MagicMock()
        mock_service.get_city_by_ip.side_effect = Exception("IP resolution error")
        mock_service.get_weather.return_value = {"error": {"message": "City not found"}}
        mock_service_cls.return_value = mock_service

        Main().run()

        captured = capsys.readouterr()
        assert "[-] {'message': 'City not found'}" in captured.out

    @patch("weatherender.CLI.main.platform.system", return_value="Windows")
    @patch("weatherender.CLI.main.subprocess.run")
    def test_print_file_windows_success(self, mock_run, mock_system, capsys, tmp_path):
        path = tmp_path / "weather_report.txt"
        path.write_text("report")
        mock_run.return_value = MagicMock(returncode=0)

        print_file(path)

        assert "[+] Sent to printer (Windows)" in capsys.readouterr().out

    @patch("weatherender.CLI.main.shutil.which", return_value="/usr/bin/lp")
    @patch("weatherender.CLI.main.platform.system", return_value="Linux")
    @patch("weatherender.CLI.main.subprocess.run")
    def test_print_file_lp_falls_back_to_printer(
        self, mock_run, mock_system, mock_which, capsys, tmp_path
    ):
        path = tmp_path / "weather_report.txt"
        path.write_text("report")
        mock_run.side_effect = [
            MagicMock(returncode=1, stderr="bad printer", stdout=""),
            MagicMock(returncode=0, stdout="MyPrinter"),
            MagicMock(returncode=0, stdout="sent"),
        ]

        print_file(path)

        output = capsys.readouterr().out
        assert "Trying printer: MyPrinter" in output
        assert "[+] Sent to printer" in output

    @patch("weatherender.CLI.main.shutil.which", return_value="/usr/bin/lp")
    @patch("weatherender.CLI.main.platform.system", return_value="Linux")
    @patch("weatherender.CLI.main.subprocess.run")
    def test_print_file_no_printers_found(
        self, mock_run, mock_system, mock_which, capsys, tmp_path
    ):
        path = tmp_path / "weather_report.txt"
        path.write_text("report")
        mock_run.side_effect = [
            MagicMock(returncode=1, stdout="", stderr="failed"),
            MagicMock(returncode=0, stdout=""),
        ]

        print_file(path)

        assert "[-] No printers found on this system" in capsys.readouterr().out

    def test_weather_report_color_metrics_handles_missing_forecast_data(self):
        data = {
            "location": {
                "localtime": "2026-07-16 12:00",
                "name": "Berlin",
                "country": "Germany",
            },
            "current": {
                "temp_c": -5,
                "uv": 8,
                "pressure_mb": 800,
                "wind_kph": 70,
                "condition": {"text": "Snow"},
            },
            "forecast": {"forecastday": []},
        }
        report = WeatherReport(data, for_printing=False)
        metrics = report.get_color_metrics()
        assert len(metrics) == 5
        assert all(isinstance(value, str) for value in metrics)
