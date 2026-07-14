import requests
import unittest
from unittest.mock import patch, Mock
from services import WeatherService

class TestWeatherService(unittest.TestCase):
    @patch("services.requests.get")
    def test_ip_none_returns_moscow_without_network_call(self, mock_get):
        city = WeatherService.get_city_by_ip(None)
        assert city == "Moscow"
        mock_get.assert_not_called()
    @patch("services.requests.get")
    def test_ip_geo_success_from_ip_api(self, mock_get):
        mock_response = Mock(status_code=200)
        mock_get.return_value = mock_response
        mock_response.json.return_value = {"status": "success", "city": "Berlin"}
        city = WeatherService.get_city_by_ip("8.8.8.8")
        assert city == "Berlin"
        assert mock_get.call_count == 1
    @patch("services.requests.get")
    def test_ip_localhost_returns_moscow(self, mock_get):
        city = WeatherService.get_city_by_ip("127.0.0.1")
        assert city == "Moscow"
        mock_get.assert_not_called()