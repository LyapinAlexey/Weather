import unittest
from unittest.mock import Mock, patch

import requests
from requests.models import Response

from weatherender.services import WeatherService


class TestGetCityByIp(unittest.TestCase):
    @patch("weatherender.services.requests.get")
    def test_ip_none_returns_moscow_without_network_call(self, mock_get):
        city = WeatherService.get_city_by_ip(None)
        assert city == "London"
        mock_get.assert_not_called()

    @patch("weatherender.services.requests.get")
    def test_ip_geo_success_from_ip_api(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.json.return_value = {
            "status": "success",
            "lat": 52.5200,
            "lon": 13.4050,
        }
        mock_get.return_value = mock_response

        result = WeatherService.get_city_by_ip("8.8.8.8")
        assert result == "52.52,13.405"

    @patch("weatherender.services.requests.get")
    def test_ip_localhost_returns_moscow(self, mock_get):
        city = WeatherService.get_city_by_ip("127.0.0.1")
        assert city == "London"
        mock_get.assert_not_called()

    @patch("weatherender.services.requests.get")
    def test_ip_geo_falls_back_to_ipinfo_on_ipapi_fail(self, mock_get):
        mock_ipapi_fail = Mock(status_code=400)
        mock_ipinfo_success = Mock(status_code=200)
        mock_ipinfo_success.json.return_value = {"city": "London"}
        mock_get.side_effect = [mock_ipapi_fail, mock_ipinfo_success]
        city = WeatherService.get_city_by_ip("8.8.8.8")
        assert city == "London"
        assert mock_get.call_count == 2

    @patch("weatherender.services.requests.get")
    def test_ip_geo_returns_default_moscow_when_all_fail(self, mock_get):
        mock_ipapi_fail = Mock(status_code=500)
        mock_ipinfo_fail = Mock(status_code=404)
        mock_ipapi_fail.json.return_value = {"city": "Dublin"}
        mock_get.side_effect = [mock_ipapi_fail, mock_ipinfo_fail]
        city = WeatherService.get_city_by_ip("8.8.8.8")
        assert city == "London"
        assert mock_get.call_count == 2

    @patch("weatherender.services.requests.get")
    def test_ip_geo_falls_back_to_ipinfo_on_exception(self, mock_get):
        ipapi_err = requests.RequestException("Connection lost")
        mock_ipinfo_success = Mock(status_code=200)
        mock_ipinfo_success.json.return_value = {"city": "London"}
        mock_get.side_effect = [ipapi_err, mock_ipinfo_success]
        city = WeatherService.get_city_by_ip("8.8.8.8")
        assert city == "London"
        assert mock_get.call_count == 2

    @patch("weatherender.services.requests.get")
    def test_ip_geo_ipapi_status_fail_falls_back_to_ipinfo(self, mock_get):
        mock_ipapi = Mock(status_code=200)
        mock_ipapi.json.return_value = {"status": "fail"}
        mock_ipinfo = Mock(status_code=200)
        mock_ipinfo.json.return_value = {"city": "London"}

        mock_get.side_effect = [mock_ipapi, mock_ipinfo]
        city = WeatherService.get_city_by_ip("8.8.8.8")
        assert city == "London"
        assert mock_get.call_count == 2

    @patch("weatherender.services.requests.get")
    def test_ip_geo_both_services_raise_exception(self, mock_get):
        mock_get.side_effect = [
            requests.RequestException("ip-api down"),
            requests.RequestException("ipinfo down"),
        ]
        city = WeatherService.get_city_by_ip("8.8.8.8")
        assert city == "London"
        assert mock_get.call_count == 2

    @patch("weatherender.services.requests.get")
    def test_ip_geo_ipinfo_missing_city_key_returns_default(self, mock_get):
        mock_ipapi = Mock(status_code=400)
        mock_ipinfo = Mock(status_code=200)
        mock_ipinfo.json.return_value = {}

        mock_get.side_effect = [mock_ipapi, mock_ipinfo]
        city = WeatherService.get_city_by_ip("8.8.8.8")
        assert city == "London"


class TestGetWeather(unittest.TestCase):
    @patch("weatherender.services.requests.get")
    @patch("weatherender.services.Config")
    def test_weather_missing_api_key_returns_error(self, mock_config, mock_get):
        mock_config.WEATHER_API_KEY = None
        res = WeatherService.get_weather("London", api_key=None)
        assert "API key" in res["error"]["message"]
        mock_get.assert_not_called()

    @patch("weatherender.services.requests.get")
    def test_weather_invalid_key_returns_error(self, mock_get):
        mock_responce = Mock(status_code=401)
        mock_get.return_value = mock_responce
        res = WeatherService.get_weather("London", api_key="fake-invalid-key")
        assert "Invalid API key" in res["error"]["message"]
        assert mock_get.call_count == 1

    @patch("weatherender.services.requests.get")
    def test_weather_city_not_found_returns_error(self, mock_get):
        mock_responce = Mock(status_code=400)
        mock_get.return_value = mock_responce
        res = WeatherService.get_weather("London", api_key="fake-invalid-key")
        assert "City 'London' not found." in res["error"]["message"]
        assert mock_get.call_count == 1

    @patch("weatherender.services.requests.get")
    def test_weather_success_returns_json(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_response.headers.get.return_value = "application/json"
        mock_response.json.return_value = {"current": {"temp_c": "33"}}
        mock_get.return_value = mock_response
        res = WeatherService.get_weather("London", api_key="fake-invalid-key")
        assert res["current"]["temp_c"] == "33"
        assert mock_get.call_count == 1

    @patch("weatherender.services.requests.get")
    def test_weather_network_error_returns_error(self, mock_get):
        mock_get.side_effect = requests.RequestException("Connection lost")
        res = WeatherService.get_weather("London", api_key="fake-invalid")
        assert "Network error" in res["error"]["message"]
        assert mock_get.call_count == 1

    @patch("weatherender.services.requests.get")
    def test_weather_server_error_500_returns_error(self, mock_get):
        real_response = Response()
        real_response.status_code = 500
        real_response._content = b'{"error": {"message": "Server Error"}}'

        mock_get.return_value = real_response

        res = WeatherService.get_weather("London", api_key="fake-key")
        assert "error" in res

    @patch("weatherender.services.requests.get")
    def test_weather_invalid_json_response(self, mock_get):
        real_response = Response()
        real_response.status_code = 200
        real_response._content = b"Invalid JSON String"

        mock_get.return_value = real_response

        res = WeatherService.get_weather("London", api_key="fake-key")
        assert "error" in res

    @patch("weatherender.services.requests.get")
    def test_weather_generic_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Unexpected network error")

        res = WeatherService.get_weather("London", api_key="fake-key")
        assert "error" in res

    @patch(
        "weatherender.services.cache_service.get",
        return_value={"current": {"temp_c": 12}},
    )
    def test_weather_returns_cached_value_without_api_call(self, mock_cache_get):
        result = WeatherService.get_weather("London", api_key="fake-key")

        assert result["current"]["temp_c"] == 12
        mock_cache_get.assert_called_once_with("weather:london")

    @patch("weatherender.services.cache_service.get", return_value=None)
    @patch("weatherender.services.requests.get")
    def test_weather_invalid_content_type_returns_error(self, mock_get, mock_cache_get):
        response = Mock(status_code=200)
        response.headers.get.return_value = "text/plain"
        mock_get.return_value = response

        result = WeatherService.get_weather("London", api_key="fake-key")

        assert "invalid response format" in result["error"]["message"]
        mock_cache_get.assert_called_once_with("weather:london")

    @patch("weatherender.services.cache_service.get", return_value=None)
    @patch("weatherender.services.requests.get")
    def test_weather_parsing_error_returns_error(self, mock_get, mock_cache_get):
        response = Mock(status_code=200)
        response.headers.get.return_value = "application/json"
        response.json.side_effect = ValueError("bad json")
        mock_get.return_value = response

        result = WeatherService.get_weather("London", api_key="fake-key")

        assert "check your internet connection" in result["error"]["message"]
        mock_cache_get.assert_called_once_with("weather:london")

    @patch("weatherender.services.cache_service.get", return_value=None)
    @patch("weatherender.services.cache_service.set")
    @patch("weatherender.services.requests.get")
    def test_weather_coordinates_are_accepted_and_cached(
        self, mock_get, mock_cache_set, mock_cache_get
    ):
        response = Mock(status_code=200)
        response.headers.get.return_value = "application/json"
        response.json.return_value = {"current": {"temp_c": 22}}
        mock_get.return_value = response

        result = WeatherService.get_weather((50.0, 14.0), api_key="fake-key")

        assert result["current"]["temp_c"] == 22
        mock_cache_get.assert_called_once_with("weather:50.0,14.0")
        mock_cache_set.assert_called_once_with(
            "weather:50.0,14.0", {"current": {"temp_c": 22}}
        )

    @patch("weatherender.services.cache_service.get", return_value=None)
    @patch("weatherender.services.requests.get")
    def test_get_city_by_ip_detects_robot_provider(self, mock_get, mock_cache_get):
        ipapi_response = Mock(status_code=200)
        ipapi_response.json.return_value = {
            "status": "success",
            "org": "Amazon Web Services",
            "as": "AS12345",
            "lat": 48.8584,
            "lon": 2.2945,
        }
        mock_get.return_value = ipapi_response

        result = WeatherService.get_city_by_ip("8.8.8.8")

        assert result == "Robot-Datacenter"
        mock_cache_get.assert_not_called()

    @patch("weatherender.services.cache_service.get", return_value=None)
    @patch("weatherender.services.requests.get")
    def test_get_city_by_ip_uses_ipinfo_coordinates(self, mock_get, mock_cache_get):
        ipapi_response = Mock(status_code=400)
        ipinfo_response = Mock(status_code=200)
        ipinfo_response.json.return_value = {
            "org": "Example ISP",
            "loc": "51.5074,-0.1278",
        }
        mock_get.side_effect = [ipapi_response, ipinfo_response]

        result = WeatherService.get_city_by_ip("8.8.8.8")

        assert result == (51.5074, -0.1278)
        mock_cache_get.assert_not_called()

    @patch("weatherender.services.requests.get")
    def test_get_city_by_ip_strips_csv_ip_and_uses_lat_lon(self, mock_get):
        ipapi_response = Mock(status_code=200)
        ipapi_response.json.return_value = {
            "status": "success",
            "org": "Example ISP",
            "as": "AS12345",
            "lat": 41.40338,
            "lon": 2.17403,
        }
        mock_get.return_value = ipapi_response

        result = WeatherService.get_city_by_ip("8.8.8.8, 123.4.5.6")

        assert result == "41.40338,2.17403"
        mock_get.assert_called_once_with("http://ip-api.com/json/8.8.8.8", timeout=3)

    @patch("weatherender.services.requests.get")
    def test_get_city_by_ip_returns_london_when_ipinfo_loc_missing(self, mock_get):
        ipapi_response = Mock(status_code=200)
        ipapi_response.json.return_value = {"status": "fail"}
        ipinfo_response = Mock(status_code=200)
        ipinfo_response.json.return_value = {"org": "Example ISP"}
        mock_get.side_effect = [ipapi_response, ipinfo_response]

        assert WeatherService.get_city_by_ip("8.8.8.8") == "London"

    @patch("weatherender.services.cache_service.get", return_value=None)
    @patch("weatherender.services.requests.get")
    def test_get_elevation_is_cached_and_returns_float(self, mock_get, mock_cache_get):
        mock_cache_get.return_value = "123.45"

        result = WeatherService.get_elevation(12.0, 34.0)

        assert result == 123.45
        mock_cache_get.assert_called_once_with("elevation:12.0:34.0")
        mock_get.assert_not_called()

    @patch("weatherender.services.cache_service.get", return_value=None)
    @patch("weatherender.services.cache_service.set")
    @patch("weatherender.services.requests.get")
    def test_get_elevation_fetches_api_and_caches_result(
        self, mock_get, mock_cache_set, mock_cache_get
    ):
        response = Mock(status_code=200)
        response.json.return_value = {"elevation": [123.45]}
        mock_get.return_value = response

        result = WeatherService.get_elevation(12.0, 34.0)

        assert result == 123.45
        mock_cache_get.assert_called_once_with("elevation:12.0:34.0")
        mock_cache_set.assert_called_once_with("elevation:12.0:34.0", 123.45, ttl=86400)

    @patch("weatherender.services.cache_service.get", return_value=None)
    @patch("weatherender.services.requests.get")
    def test_weather_generic_server_error_returns_message(
        self, mock_get, _mock_cache_get
    ):
        response = Mock(status_code=503)
        response.headers.get.return_value = "application/json"
        mock_get.return_value = response

        result = WeatherService.get_weather("London", api_key="fake-key")

        assert "Weather service error. Status code: 503" == result["error"]["message"]
