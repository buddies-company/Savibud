from adapters.ports.transaction_repository import (
    TransactionRepository as TransactionRepositoryBase,
)
from adapters.postgres.crud import CRUD
from entities.transaction import Transaction


class TransactionRepository(TransactionRepositoryBase, CRUD):
    """Transaction Repository using Postgres (SQLModel) data"""

    def __init__(self, session):
        super().__init__(session, Transaction)

    def upsert_transaction(self, account_id, transaction_data):
        """Insert or update a transaction for the given account."""
        statement = self.session.select(Transaction).where(
            Transaction.account_id == account_id,
            Transaction.powens_transaction_id == transaction_data["id"],
        )
        existing_tx = self.session.exec(statement).first()

        if existing_tx:
            # Update existing transaction
            existing_tx.amount = transaction_data.get("amount", existing_tx.amount)
            existing_tx.label = transaction_data.get("label", existing_tx.label)
            existing_tx.raw_data = transaction_data
            self.session.add(existing_tx)
        else:
            # Create new transaction
            new_tx = Transaction(
                account_id=account_id,
                powens_transaction_id=transaction_data["id"],
                amount=transaction_data["amount"],
                label=transaction_data["label"],
                raw_data=transaction_data,
            )
            self.session.add(new_tx)
