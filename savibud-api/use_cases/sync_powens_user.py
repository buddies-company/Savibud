from uuid import UUID

from adapters.ports.powens_repository import PowensRepository
from adapters.ports.saving_repository import SavingsAutomationRepository
from adapters.ports.transaction_repository import TransactionRepository
from adapters.powens.client import PowensClient


class SyncUserData:
    def __init__(
        self,
        powens_client: PowensClient,
        repo: SavingsAutomationRepository,
        powens_repo: PowensRepository,
        transaction_repo: TransactionRepository,
    ):
        self.powens = powens_client
        self.repo = repo
        self.powens_repo = powens_repo
        self.transaction_repo = transaction_repo

    def execute(self, user_id: UUID):

        conn = self.powens_repo.read(user_id=user_id)[0]
        raw_accounts = self.powens.get_accounts(conn.powens_access_token)

        for acc in raw_accounts["accounts"]:
            self.repo.upsert_account(user_id, acc)
            # Fetch transactions for each account
            raw_txs = self.powens.get_transactions(conn.powens_access_token, acc["id"])
            for tx in raw_txs["transactions"]:
                self.transaction_repo.upsert_transaction(acc["id"], tx)
