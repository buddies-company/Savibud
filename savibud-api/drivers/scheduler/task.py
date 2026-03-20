import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from adapters.postgres.saving_repository import SavingsGoalRepository
from drivers.database import SessionLocal
from use_cases.process_monthly_savings import ProcessMonthlySavings

logger = logging.getLogger(__name__)


def _run_monthly_savings() -> None:
    """Job wrapper that creates a DB session and executes the use case."""
    # We use a context manager for cleaner code
    with SessionLocal() as db:
        try:
            repo = SavingsGoalRepository(db)
            use_case = ProcessMonthlySavings(repo)

            use_case.execute()

            db.commit()
            logger.info("✅ Monthly savings job completed successfully.")
        except Exception:
            db.rollback()
            logger.exception("❌ Monthly savings job failed")


def register_jobs(scheduler: AsyncIOScheduler) -> None:
    """Register savings-related jobs on the provided scheduler."""
    # Run every day at midnight
    scheduler.add_job(
        _run_monthly_savings,
        trigger="cron",
        hour=0,
        minute=0,
        id="process_monthly_savings",
        replace_existing=True,
        # Allow the job to run even if it's up to 24 hours late
        misfire_grace_time=86400,
        # coalesce=True prevents it from running 10 times if it missed 10 days
        coalesce=True,
    )
    logger.info("📅 Job registered: process_monthly_savings (Cron: 00:00)")
