import logging
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from models import SessionLocal, WeatherRequest
from logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
def clear() -> None:
    # datetime.now(timezone.utc) + replace(tzinfo=None) instead of deprecated utcnow();
    # stays naive to match models.py created_at (which is also naive) — avoiding schema migration
    cutoff_date = datetime.now(timezone.utc).replace(tzinfo=None) - relativedelta(months=1)
    db_session =  SessionLocal()
    try:
        result = db_session.query(WeatherRequest).filter(WeatherRequest.created_at < cutoff_date).delete()
        db_session.commit()
        logger.info(f"Cleared files: {result}")
    except Exception as e:
        logger.error(f"Error while clearing database: {e}")
        db_session.rollback()
    finally:
        db_session.close()

if __name__ == "__main__":
    clear()