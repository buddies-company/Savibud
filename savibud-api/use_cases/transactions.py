from typing import Optional
from uuid import UUID
from entities.transaction import Transaction
from adapters.ports.transaction_repository import TransactionRepository


class TransactionInteractor:
    def __init__(self, transaction_repo: TransactionRepository):
        self.repo = transaction_repo

    def list_transactions(self, **kwargs):
        """Proxy to the repository's optimized search."""
        return self.repo.get_user_transactions(**kwargs)

    def create_transaction(self, user_id: UUID, item: Transaction) -> Transaction:
        """Create a new transaction owned by the given user."""
        # Validation: transaction cannot have both category and savings goal
        if item.category_id and item.savings_goal_id:
            raise ValueError("Transaction cannot have both a category and a savings goal")
        
        item.user_id = user_id
        return self.repo.create(item)

    def update_transaction(self, tx_id: int, user_id: UUID, **modifications) -> Optional[Transaction]:
        """Update a transaction after applying business rules.

        Important rule: transactions that originate from Powens (have a
        `powens_transaction_id`) must not have their `date` or `amount`
        modified by users. We silently drop those fields from the
        modifications before persisting.
        """
        tx = self.repo.get_by_id_and_user(tx_id, user_id)
        if not tx:
            return None

        # Validation: transaction cannot have both category and savings goal
        final_category_id = modifications.get('category_id', tx.category_id)
        final_savings_goal_id = modifications.get('savings_goal_id', tx.savings_goal_id)
        if final_category_id and final_savings_goal_id:
            raise ValueError("Transaction cannot have both a category and a savings goal")

        # Prevent changing amount/date for Powens-linked transactions
        if getattr(tx, "powens_transaction_id", None):
            modifications.pop("amount", None)
            modifications.pop("date", None)

        if not modifications:
            return tx

        return self.repo.update(tx_id, **modifications)

    def toggle_internal_status(self, tx_id: int, user_id: UUID) -> Optional[Transaction]:
        """Business logic: find, verify, and flip the boolean."""
        tx = self.repo.get_by_id_and_user(tx_id, user_id)
        if not tx:
            return None

        new_status = not tx.is_internal
        return self.repo.update(tx_id, is_internal=new_status)