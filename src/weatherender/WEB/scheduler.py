import os

from apscheduler.schedulers.background import BackgroundScheduler

from weatherender.dbclear import clear
from weatherender.logging_config import logging
from weatherender.models import SessionLocal

LOCK_PATH = "/tmp/dbclear_scheduler.lock"
logger = logging.getLogger(__name__)


def try_acquire_leadership(lock_path: str) -> bool:
    """Attempt to acquire a file-based lock to act as the primary scheduler leader."""
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
        return True
    except FileExistsError:
        return False


def run_dbclear_job() -> None:
    """Job function that creates a database session to clear old weather requests."""
    session = SessionLocal()
    try:
        clear(session)
        logger.info("Weekly database clear job executed successfully.")
    except Exception:
        logger.exception("Error executing weekly database clear job")
    finally:
        session.close()


def init_scheduler() -> None:
    """Initialize and start the background job scheduler to run weekly database cleanup tasks."""
    if not try_acquire_leadership(LOCK_PATH):
        logger.info("Skipping scheduler initialization: another worker is the leader.")
        return

    scheduler = BackgroundScheduler()
    scheduler.add_job(run_dbclear_job, "interval", days=7)
    scheduler.start()
    logger.info("Scheduler started successfully")
