import asyncio
import logging
import signal
from datetime import datetime

import httpx
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import timezone

from adapters.postgres.account_repository import (
    AccountRepository,
    SnapshotAccountRepository,
)
from adapters.postgres.powens_repository import PowensRepository
from adapters.postgres.saving_repository import SavingsGoalRepository
from adapters.postgres.transaction_repository import TransactionRepository
from adapters.powens.client import PowensClient
from drivers.config import settings
from drivers.database import SessionLocal
from drivers.scheduler.task import register_jobs
from scheduler.internal_transactions import auto_flag_internal
from use_cases.sync_powens_user import SyncUserData

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("savibud.scheduler")

# --- GLOBAL SCHEDULER OBJECT (NOT STARTED YET) ---
jobstores = {"default": SQLAlchemyJobStore(url=settings.database_url)}
# We define it here so other functions can reference it, but we DON'T start it yet.
paris_tz = timezone("Europe/Paris")

scheduler = AsyncIOScheduler(jobstores=jobstores, timezone=paris_tz)


# --- TASK 1: BANK SYNC ---
async def sync_all_banks():
    """Fetches new data from Powens for all connected users using the central use-case."""
    logger.info("🚀 [TASK START] Starting global bank synchronization...")

    with SessionLocal() as db:
        try:
            powens_repo = PowensRepository(db)
            account_repo = AccountRepository(db)
            snapshot_account_repo = SnapshotAccountRepository(db)
            transaction_repo = TransactionRepository(db)
            savings_repo = SavingsGoalRepository(db)

            connections = powens_repo.read()
            logger.info(
                f"📊 [DEBUG] Found {len(connections)} active Powens connections."
            )


            loop = asyncio.get_running_loop()
            for conn in connections:
                try:
                    logger.info(f"🔄 Syncing User ID: {conn.user_id}")
                    powens_client = PowensClient(
                        access_token=conn.powens_access_token,
                        domain=settings.powens_domain,
                    )

                    sync_user = SyncUserData(
                        powens_client=powens_client,
                        repo=savings_repo,
                        powens_repo=powens_repo,
                        transaction_repo=transaction_repo,
                        account_repo=account_repo,
                        snapshot_account_repo=snapshot_account_repo,
                    )
                    # Run synchronous use-case in threadpool to avoid blocking the event loop
                    await loop.run_in_executor(
                        None, sync_user.accounts_sync, conn.user_id
                    )
                    db.commit()
                    auto_flag_internal(db, conn.user_id)
                except Exception as e:
                    db.rollback()
                    logger.error(f"❌ Error syncing user {conn.user_id}: {str(e)}")

            logger.info("🏁 [TASK END] Global bank sync completed.")
        except Exception as e:
            logger.error(f"🔥 Critical Failure: {str(e)}")


# --- DEBUG HELPERS ---
def print_scheduler_status():
    jobs = scheduler.get_jobs()
    print("\n" + "═" * 60)
    print(f" 🛠️  SAVIBUD SCHEDULER DEBUG - {datetime.now().strftime('%H:%M:%S')}")
    print("─" * 60)
    for job in jobs:
        print(f" • ID: {job.id} | Next Run: {job.next_run_time}")
    print("═" * 60 + "\n")


# --- MAIN ASYNC LOOP ---
async def main():
    logger.info("Starting Savibud Worker Process...")

    # REQUIRED: start() must be called inside the loop initialized by asyncio.run()
    scheduler.start()

    # Add/Update the Bank Sync job
    scheduler.add_job(
        sync_all_banks,
        trigger="cron",
        hour=3,
        id="global_bank_sync",
        replace_existing=True,
        next_run_time=datetime.now(),  # Runs immediately for test
        # Allow the job to run even if it's up to 24 hours late
        misfire_grace_time=86400,
        # coalesce=True prevents it from running 10 times if it missed 10 days
        coalesce=True,
    )

    register_jobs(scheduler)

    print_scheduler_status()

    # Handle Docker/System shutdown signals gracefully
    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    # We set the event when a termination signal is received
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    logger.info("Scheduler is running. Waiting for exit signal...")

    # Instead of while True, we wait for the stop_event
    await stop_event.wait()

    logger.info("Worker shutting down gracefully...")
    scheduler.shutdown()


if __name__ == "__main__":
    try:
        # This starts the event loop and runs main()
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
