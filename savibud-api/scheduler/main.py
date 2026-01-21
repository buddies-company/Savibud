import asyncio
import logging
import signal
from datetime import datetime

import httpx
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from adapters.postgres.account_repository import AccountRepository, SnapshotAccountRepository
from adapters.postgres.powens_repository import PowensRepository
from adapters.postgres.saving_repository import SavingsAutomationRepository
from adapters.postgres.transaction_repository import TransactionRepository
from drivers.config import settings
from drivers.database import SessionLocal
from drivers.scheduler.task import register_jobs
from entities.account import Account as DomainAccount, SnapshotAccount
from entities.budget import Budget
from entities.category import Category
from entities.transaction import Transaction as DomainTransaction
from entities.user import User
from scheduler.internal_transactions import auto_flag_internal

# --- LOGGING CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("savibud.scheduler")

# --- GLOBAL SCHEDULER OBJECT (NOT STARTED YET) ---
jobstores = {"default": SQLAlchemyJobStore(url=settings.database_url)}
# We define it here so other functions can reference it, but we DON'T start it yet.
scheduler = AsyncIOScheduler(jobstores=jobstores)


# --- TASK 1: BANK SYNC ---
async def sync_all_banks():
    """Fetches new data from Powens for all connected users"""
    logger.info("🚀 [TASK START] Starting global bank synchronization...")

    with SessionLocal() as db:
        try:
            powens_repo = PowensRepository(db)
            account_repo = AccountRepository(db)
            snapshot_account_repo = SnapshotAccountRepository(db)
            transaction_repo = TransactionRepository(db)

            connections = powens_repo.read()
            logger.info(
                f"📊 [DEBUG] Found {len(connections)} active Powens connections."
            )

            async with httpx.AsyncClient(timeout=30.0) as client:
                for conn in connections:
                    try:
                        logger.info(f"🔄 Syncing User ID: {conn.user_id}")
                        headers = {
                            "Authorization": f"Bearer {conn.powens_access_token}"
                        }

                        acc_resp = await client.get(
                            f"https://{settings.powens_domain}/2.0/users/me/accounts",
                            headers=headers,
                        )

                        if acc_resp.status_code != 200:
                            continue

                        accounts = acc_resp.json().get("accounts", [])
                        for acc in accounts:
                            db_acc_data = {
                                "powens_account_id": acc["id"],
                                "user_id": conn.user_id,
                                "bank_name": acc.get("name", "Unknown"),
                                "account_type": acc.get("type", "unknown"),
                                "balance": acc.get("balance", 0),
                                "raw_data": acc,
                                "last_sync": datetime.now(),
                            }

                            existing_acc = account_repo.read(
                                powens_account_id=str(acc["id"]), user_id=conn.user_id
                            )
                            if existing_acc:
                                db_account = account_repo.update(
                                    existing_acc[0].id, **db_acc_data
                                )
                            else:
                                db_account = account_repo.create(
                                    DomainAccount(**db_acc_data)
                                )
                            db_snap_acc_data = {
                                "account_id": db_account.id,
                                "balance": acc.get("balance", 0),
                                "snapshot_date": datetime.now(),
                            }
                            snapshot_account_repo.create(
                                SnapshotAccount(**db_snap_acc_data)
                            )

                            if not db_account:
                                logger.warning(
                                    f"⚠️ Failed to create or update account for Powens ID: {acc['id']}"
                                )
                                continue

                            tx_resp = await client.get(
                                f"https://{settings.powens_domain}/2.0/users/me/accounts/{acc['id']}/transactions",
                                params={"limit": 1000, "offset": 0},
                                headers=headers,
                            )

                            if tx_resp.status_code == 200:
                                for tx in tx_resp.json().get("transactions", []):
                                    if not transaction_repo.read(
                                        powens_transaction_id=str(tx["id"])
                                    ):
                                        transaction_repo.create(
                                            DomainTransaction(
                                                powens_transaction_id=tx["id"],
                                                user_id=conn.user_id,
                                                account_id=db_account.id,
                                                amount=tx.get("value", 0),
                                                label=tx.get("original_wording", ""),
                                                date=tx.get("date"),
                                                raw_data=tx,
                                            )
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
        coalesce=True
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
