from datetime import date as date_type
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from adapters.ports.powens_repository import PowensRepository
from adapters.ports.rule_repository import RuleRepository
from adapters.ports.saving_repository import SavingsGoalRepository, SavingsGoalRepository
from adapters.ports.transaction_repository import TransactionRepository
from adapters.ports.account_repository import (
    AccountRepository,
    SnapshotAccountRepository,
)
from adapters.powens.client import PowensClient
from entities.account import Account, SnapshotAccount
from entities.powens import PowensConnection
from entities.transaction import Transaction
from use_cases.rule_engine import RuleEngine
from use_cases.recalculate_savings import RecalculateSavingsGoals


class SyncUserData:
    def __init__(
        self,
        powens_client: PowensClient,
        repo: SavingsGoalRepository,
        powens_repo: PowensRepository,
        transaction_repo: TransactionRepository,
        account_repo: AccountRepository,
        snapshot_account_repo: SnapshotAccountRepository,
        rule_repo: RuleRepository| None = None,
        savings_goal_repo: SavingsGoalRepository| None = None,
    ):
        self.powens = powens_client
        self.repo = repo
        self.powens_repo = powens_repo
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.snapshot_account_repo = snapshot_account_repo
        self.rule_engine = RuleEngine(rule_repo) if rule_repo else None
        self.recalculate_savings = RecalculateSavingsGoals(savings_goal_repo, transaction_repo) if savings_goal_repo else None

    def accounts_sync(self, user_id: UUID):
        """Sync all accounts for a user from Powens API."""
        conn = self.powens_repo.read(user_id=user_id)[0]
        raw_accounts = self.powens.get_accounts()

        for acc in raw_accounts["accounts"]:
            self._sync_account(user_id, conn, acc)

    def account_sync(self, user_id: UUID, account_id: str):
        """Sync a specific account for a user from Powens API."""
        conn = self.powens_repo.read(user_id=user_id)[0]
        raw_account = self.powens.get_account(account_id)

        self._sync_account(user_id, conn, raw_account)

    def _sync_account(self, user_id: UUID, conn: PowensConnection, raw_account: dict):
        temp_account = Account(
            **{
                "powens_account_id": str(raw_account["id"]),
                "user_id": conn.user_id,
                "name": raw_account.get("name", "Unknown"),
                "account_type": raw_account.get("type", "unknown"),
                "balance": raw_account.get("balance", 0),
                "raw_data": raw_account,
                "last_sync": datetime.now(),
            }
        )
        existing = self.account_repo.read(user_id=user_id, powens_account_id=str(raw_account["id"]))

        if not existing or existing[0].bank_name == "Unknown":
            banks = self.powens.get_banks(raw_account.get("id_connection"))
            temp_account.bank_name = banks.get("name", "Unknown")

        self.account_repo.upsert(
            temp_account, user_id=user_id, powens_account_id=str(raw_account["id"])
        )
        # Fetch the database account by Powens ID to get its UUID
        db_accounts = self.account_repo.read(
            powens_account_id=str(raw_account["id"]), user_id=user_id
        )
        if not db_accounts:
            return
        db_account = db_accounts[0]
        self.snapshot_account_repo.create(
            SnapshotAccount(
                **{
                    "user_id": conn.user_id,
                    "account_id": db_account.id,
                    "balance": raw_account.get("balance", 0),
                    "snapshot_date": datetime.now(),
                }
            )
        )
        raw_txs = self.powens.get_transactions(str(db_account.powens_account_id))
        for tx in raw_txs["transactions"]:
            # Parse date string to date object if it's a string
            tx_date = tx.get("date", None)
            if isinstance(tx_date, str):
                tx_date = date_type.fromisoformat(tx_date)
            
            temp_tx = Transaction(
                **{
                    "powens_transaction_id": str(tx["id"]),
                    "account_id": db_account.id,
                    "user_id": conn.user_id,
                    "amount": Decimal(str(tx.get("value", 0))),
                    "date": tx_date,
                    "label": tx.get("original_wording", ""),
                    "raw_data": tx,
                }
            )
            
            # Apply categorization rules
            if self.rule_engine:
                temp_tx = self.rule_engine.apply_rules(temp_tx, user_id)
            
            self.transaction_repo.upsert(
                temp_tx,
                user_id=user_id,
                account_id=db_account.id,
                powens_transaction_id=str(tx["id"]),
            )
        
        # Recalculate savings goals after all transactions are synced
        if self.recalculate_savings:
            self.recalculate_savings(user_id)
