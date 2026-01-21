from datetime import timedelta
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from entities.account import Account
from entities.transaction import Transaction


def auto_flag_internal(db: Session, user_id: UUID):
    """
    Scans recent transactions to identify and link internal transfers
    (e.g., from Checking to Savings).
    """
    # 1. Get all potential 'Transfer' candidates from the last 7 days
    # (7 days allows for bank processing delays between different institutions)
    lookback_date = func.now() - timedelta(days=7)

    # Fetch unlinked transactions for this user
    # We join with Account to ensure we only look at this user's data
    candidates = (
        db.query(Transaction)
        .join(Account)
        .filter(
            Account.user_id == user_id,
            Transaction.date >= lookback_date,
            Transaction.is_internal == False,
            Transaction.internal_link_id == None,
        )
        .all()
    )

    linked_ids = set()

    for tx_a in candidates:
        if tx_a.id in linked_ids:
            continue

        # 2. Search for the 'Mirror' transaction
        # Criteria:
        # - Opposite amount (tx_a.amount == -tx_b.amount)
        # - Close date (within 3 days of each other)
        # - Different accounts (can't be a transfer to the same account)
        mirror = (
            db.query(Transaction)
            .join(Account)
            .filter(
                Account.user_id == user_id,
                Account.id != tx_a.account_id,
                Transaction.id != tx_a.id,
                Transaction.amount == -tx_a.amount,
                # Date window: tx_a.date +/- 3 days
                Transaction.date >= tx_a.date - timedelta(days=3),
                Transaction.date <= tx_a.date + timedelta(days=3),
                Transaction.is_internal == False,
                Transaction.internal_link_id == None,
            )
            .first()
        )

        if mirror:
            # 3. Apply a 'Keyword' safety check (Optional but recommended)
            # Banks often use "VIR", "Transfer", "Internal" in labels
            transfer_keywords = ["vir", "transfer", "virement", "internal", "self"]
            label_a = tx_a.label.lower()
            label_b = mirror.label.lower()

            # If both have transfer keywords, we are very confident
            is_confident = any(k in label_a for k in transfer_keywords) or any(
                k in label_b for k in transfer_keywords
            )

            if is_confident:
                # 4. Link them
                tx_a.is_internal = True
                tx_a.internal_link_id = mirror.id

                mirror.is_internal = True
                mirror.internal_link_id = tx_a.id

                linked_ids.add(tx_a.id)
                linked_ids.add(mirror.id)

                print(f"🔗 Linked: {tx_a.amount}€ from {tx_a.label} to {mirror.label}")

    db.commit()
