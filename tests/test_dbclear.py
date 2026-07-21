from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from models import WeatherRequest
from dbclear import clear

class TestDBClear:
    def test_clear_deletes_old_records(self, db_session):
        old_record = WeatherRequest(
            city="London",
            source="web",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None) - relativedelta(months=5)
        )
        new_record = WeatherRequest(
            city="New York",
            source="web",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None) - relativedelta(days=5)
        )
        db_session.add_all([old_record, new_record])
        db_session.commit()
        clear(db_session)
        remaining = db_session.query(WeatherRequest).all()
        assert len(remaining) == 1
        assert remaining[0].city == "New York"
    def test_no_old_records(self, db_session):
        new_record1 = WeatherRequest(
            city="Tokio",
            source="web",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None) - relativedelta(days=5)
        )
        new_record2 = WeatherRequest(
            city="Bangkok",
            source="web",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None) - relativedelta(days=5)
        )
        db_session.add_all([new_record1, new_record2])
        db_session.commit()
        clear(db_session)
        remaining = db_session.query(WeatherRequest).all()
        cities = {r.city for r in remaining}
        assert len(cities) == 2
        assert cities == {"Tokio", "Bangkok"}
    def test_boundary_cutoff_date(self, db_session):
        boundary_record = WeatherRequest(
            city="Paris",
            source="web",
            created_at=datetime.now(timezone.utc).replace(tzinfo=None)
                       - relativedelta(months=1)
                       + relativedelta(seconds=5)
        )
        db_session.add(boundary_record)
        db_session.commit()
        clear(db_session)
        remaining = db_session.query(WeatherRequest).all()
        assert len(remaining) == 1
        assert remaining[0].city == "Paris"