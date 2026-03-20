import csv
import io
from uuid import UUID
from decimal import Decimal
from datetime import date

from adapters.ports.account_repository import ManualAccountRepository, SnapshotAccountRepository
from entities.account import ManualAccount, SnapshotAccount


class ImportSavingsFromCSV:
    """Use case to import savings account snapshots from CSV file."""

    def __init__(
        self,
        account_repo: ManualAccountRepository,
        snapshot_repo: SnapshotAccountRepository,
    ):
        self.account_repo = account_repo
        self.snapshot_repo = snapshot_repo

    def __call__(
        self,
        user_id: UUID,
        csv_content: str,
        account_name: str,
        icon: str = "PiggyBankIcon",
        color: str = "#10b981",
    ) -> tuple[ManualAccount, list[SnapshotAccount]]:
        """
        Import savings snapshots from CSV.
        
        CSV Format expected (with header):
        date,balance
        2024-01-01,1000.00
        2024-02-01,1100.00
        ...
        
        Args:
            user_id: User ID
            csv_content: CSV file content as string
            account_name: Name for the savings account
            icon: Icon name (default: PiggyBankIcon)
            color: Hex color code (default: green)
        
        Returns:
            Tuple of (created account, created snapshots)
        """
        # Parse CSV
        reader = csv.DictReader(io.StringIO(csv_content))
        snapshots_data = []
        
        for row in reader:
            try:
                snapshot_date = date.fromisoformat(row["date"].strip())
                balance = Decimal(row["balance"].strip())
                snapshots_data.append((snapshot_date, balance))
            except (ValueError, KeyError) as e:
                raise ValueError(f"Invalid CSV row: {row}. Error: {e}")
        
        if not snapshots_data:
            raise ValueError("CSV file contains no valid data")
        
        # Create account with the latest balance
        latest_date, latest_balance = snapshots_data[-1]
        account = ManualAccount(
            user_id=user_id,
            name=account_name,
            account_type="savings",
            current_balance=latest_balance,
            currency="EUR",
            icon=icon,
            color=color,
        )
        created_account = self.account_repo.create(account)
        
        # Create snapshots
        created_snapshots = []
        for snapshot_date, balance in snapshots_data:
            snapshot = SnapshotAccount(
                manual_account_id=created_account.id,
                user_id=user_id,
                balance=balance,
                snapshot_date=snapshot_date,
            )
            created_snapshot = self.snapshot_repo.create(snapshot)
            created_snapshots.append(created_snapshot)
        
        return created_account, created_snapshots
