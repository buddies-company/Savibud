from uuid import UUID
from adapters.ports.transaction_repository import TransactionRepository


class InternalTransferService:
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    def flag_transfers(self, user_id: UUID):
        """Identify and flag internal transfers for a user based on transaction patterns."""
        candidates = self.transaction_repo.get_unlinked_candidates(user_id, days=7)

        linked_ids = set()
        transfer_keywords = ["vir", "transfer", "virement", "internal", "self"]

        for tx_a in candidates:
            if tx_a.id in linked_ids:
                continue

            # 2. Use Repository to find a mirror based on business criteria
            mirror = self.transaction_repo.find_mirror_transaction(
                user_id=user_id, source_tx=tx_a, date_window=3
            )

            if mirror and mirror.id not in linked_ids:
                label_a = tx_a.label.lower()
                label_b = mirror.label.lower()

                is_confident = any(k in label_a for k in transfer_keywords) or any(
                    k in label_b for k in transfer_keywords
                )

                if is_confident:
                    # Update Entity states
                    tx_a.is_internal = True
                    tx_a.internal_link_id = mirror.id
                    mirror.is_internal = True
                    mirror.internal_link_id = tx_a.id

                    # Persist changes
                    self.transaction_repo.update(tx_a.id, tx_a)
                    self.transaction_repo.update(mirror.id, mirror)

                    linked_ids.add(tx_a.id)
                    linked_ids.add(mirror.id)
