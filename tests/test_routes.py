from unittest.mock import patch, MagicMock

class TestRoutes:
    @patch("WEB.app.SessionLocal")
    @patch("WEB.app.Config")
    def test_index_get_no_api_key_shows_key_prompt(self, mock_config, mock_session_local, client):
        mock_config.WEATHER_API_KEY = None
        mock_session_local.return_value = MagicMock()
        response = client.get("/")
        assert response.status_code == 200
        assert b"API key is missing" in response.data
    @patch("WEB.app.SessionLocal")
    @patch("WEB.app.Config")
    @patch("WEB.app.WeatherService.get_weather")
    @patch("WEB.app.WeatherService.get_city_by_ip")
    def test_index_get_success_shows_weather(self, mock_get_city, mock_get_weather, mock_config, mock_session_local, client, fake_weather_response):
        mock_config.WEATHER_API_KEY = "fake-key"
        mock_session_local.return_value = MagicMock()
        mock_get_city.return_value = "Berlin"
        mock_get_weather.return_value = fake_weather_response
        response = client.get("/")
        assert response.status_code == 200
        assert b"Berlin" in response.data
    @patch("WEB.app.SessionLocal")
    @patch("WEB.app.Config")
    @patch("WEB.app.WeatherService.get_weather")
    @patch("WEB.app.WeatherService.get_city_by_ip")
    def test_index_post_valid_city_from_form(self, mock_get_city, mock_get_weather, mock_config, mock_session_local, client, fake_weather_response):
        mock_config.WEATHER_API_KEY = "fake-key"
        mock_session_local.return_value = MagicMock()
        mock_get_weather.return_value = fake_weather_response
        response = client.post("/", data={"city": "Berlin"})
        assert response.status_code == 200
        assert b"Berlin" in response.data
        mock_get_city.assert_not_called()
    @patch("WEB.app.SessionLocal")
    @patch("WEB.app.Config")
    @patch("WEB.app.WeatherService.get_weather")
    @patch("WEB.app.WeatherService.get_city_by_ip")
    def test_index_post_invalid_city_from_form(self, mock_get_city, mock_get_weather, mock_config, mock_session_local, client):
        mock_config.WEATHER_API_KEY = "fake-key"
        mock_session_local.return_value = MagicMock()
        response = client.post("/", data={"city": ""})
        assert response.status_code == 200
        assert b"city must be a string" in response.data
        mock_get_city.assert_not_called()
    @patch("WEB.app.SessionLocal")
    @patch("WEB.app.Config")
    @patch("WEB.app.WeatherService.get_weather")
    @patch("WEB.app.WeatherService.get_city_by_ip")
    def test_index_post_city_not_found_shows_error(self, mock_get_city, mock_get_weather, mock_config, mock_session_local, client):
        mock_config.WEATHER_API_KEY = "fake-key"
        mock_session_local.return_value = MagicMock()
        mock_get_weather.return_value = {"error": {"message": "City 'Invalid-city' not found."}}
        response = client.post("/", data={"city": "Invalid-city"})
        assert response.status_code == 200
        assert b"City &#39;Invalid-city&#39; not found" in response.data # &#39; is the HTML entity for a single quote
        mock_get_city.assert_not_called()