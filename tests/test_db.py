from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

import weatherender.API.async_db
import weatherender.models
from weatherender.models import WeatherRequest


class TestDB:
    def test_create_and_read_weather_request(self, db_session):
        request = WeatherRequest(
            city="Berlin", source="web", temp_c=20, condition="sunny", success=1
        )
        db_session.add(request)
        db_session.commit()
        found = db_session.query(WeatherRequest).filter_by(city="Berlin").first()
        assert found is not None
        assert found.city == "Berlin"
        assert found.temp_c == 20
        assert found.condition == "sunny"

    def test_missing_required_field_raises_integrity_error(self, db_session):
        request = WeatherRequest(source="web", success=1)
        db_session.add(request)
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_defaults_are_applied_when_not_specified(self, db_session):
        request = WeatherRequest(city="London", source="web")
        db_session.add(request)
        db_session.commit()
        found = db_session.query(WeatherRequest).filter_by(city="London").first()
        assert found is not None
        assert found.success == 1
        assert found.created_at is not None

    def test_optional_fields_can_be_none(self, db_session):
        request = WeatherRequest(city="Monreal", source="web", success=0)
        db_session.add(request)
        db_session.commit()
        found = db_session.query(WeatherRequest).filter_by(city="Monreal").first()
        assert found.temp_c is None
        assert found.condition is None
        assert found.error_message is None

    @pytest.mark.parametrize("temp", [-50, 0, 45])
    def test_boundary_temperature_values(self, db_session, temp):
        request = WeatherRequest(city="Tokio", source="web", temp_c=temp, success=1)
        db_session.add(request)
        db_session.commit()
        found = db_session.query(WeatherRequest).filter_by(city="Tokio").first()
        assert found.temp_c == temp

    def test_delete_weather_request(self, db_session):
        request = WeatherRequest(city="Paris", source="web", success=1)
        db_session.add(request)
        db_session.commit()
        db_session.delete(request)
        db_session.commit()
        found = db_session.query(WeatherRequest).filter_by(city="Paris").first()
        assert found is None

    def test_update_weather_request(self, db_session):
        request = WeatherRequest(city="Monza", source="web", temp_c=15, success=1)
        db_session.add(request)
        db_session.commit()
        request.temp_c = 30
        db_session.commit()
        found = db_session.query(WeatherRequest).filter_by(city="Monza").first()
        assert found.temp_c == 30

    def test_models_get_engine_and_session_local(self):
        with (
            patch("weatherender.models._engine", None),
            patch("weatherender.models._session_factory", None),
            patch("weatherender.models.create_engine") as mock_create_engine,
            patch("weatherender.models.sessionmaker") as mock_sessionmaker,
        ):
            mock_engine = MagicMock()
            mock_create_engine.return_value = mock_engine

            engine = weatherender.models.get_engine()
            assert engine == mock_engine
            mock_create_engine.assert_called_once()

            session = weatherender.models.SessionLocal()
            mock_sessionmaker.assert_called_once_with(bind=mock_engine)
            assert session == mock_sessionmaker.return_value.return_value

    def test_async_db_get_engine_and_session_local(self):
        orig_engine = weatherender.API.async_db._engine
        orig_factory = weatherender.API.async_db._session_factory
        try:
            weatherender.API.async_db._engine = None
            weatherender.API.async_db._session_factory = None
            with (
                patch.object(
                    weatherender.API.async_db.Config,
                    "DATABASE_URL",
                    "postgresql://user:pass@localhost:5432/db",
                ),
                patch(
                    "weatherender.API.async_db.create_async_engine"
                ) as mock_create_async_engine,
                patch(
                    "weatherender.API.async_db.async_sessionmaker"
                ) as mock_async_sessionmaker,
            ):
                mock_engine = MagicMock()
                mock_create_async_engine.return_value = mock_engine

                engine = weatherender.API.async_db.get_engine()
                assert engine == mock_engine
                mock_create_async_engine.assert_called_once_with(
                    "postgresql+asyncpg://user:pass@localhost:5432/db",
                    pool_size=10,
                    max_overflow=20,
                )

                session = weatherender.API.async_db.AsyncSessionLocal()
                mock_async_sessionmaker.assert_called_once_with(
                    mock_engine, expire_on_commit=False
                )
                assert session == mock_async_sessionmaker.return_value.return_value
        finally:
            weatherender.API.async_db._engine = orig_engine
            weatherender.API.async_db._session_factory = orig_factory
