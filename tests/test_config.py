import importlib
import sys

import pytest

import weatherender.config
from weatherender.config import Config


class TestConfig:
    @pytest.fixture(autouse=True)
    def _restore_config(self):
        yield
        if "config" in sys.modules:
            importlib.reload(sys.modules["config"])

    def test_url_gets_normalized(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgres://user:pass@host/db")
        if "config" in sys.modules:
            importlib.reload(sys.modules["config"])
        else:
            pass

        from weatherender.config import Config

        assert Config.DATABASE_URL.startswith("postgresql://")

    def test_url_normal(self):
        assert Config.DATABASE_URL is not None
        assert "postgresql" in Config.DATABASE_URL

    def test_url_is_none(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.setattr("dotenv.load_dotenv", lambda *args, **kwargs: None)
        importlib.reload(weatherender.config)
        assert weatherender.config.Config.DATABASE_URL is None

    def test_validate_raises_when_secret_key_is_missing(self):
        original_secret = Config.SECRET_KEY
        try:
            Config.SECRET_KEY = ""
            with pytest.raises(RuntimeError, match="SECRET_KEY is not set"):
                Config.validate()
        finally:
            Config.SECRET_KEY = original_secret

    def test_validate_rejects_invalid_log_level(self):
        original_secret = Config.SECRET_KEY
        original_log_level = Config.LOG_LEVEL
        try:
            Config.SECRET_KEY = "super-secret"
            Config.LOG_LEVEL = "TRACE"
            with pytest.raises(RuntimeError, match="Invalid LOG_LEVEL"):
                Config.validate()
        finally:
            Config.SECRET_KEY = original_secret
            Config.LOG_LEVEL = original_log_level
