"""Manual accounts API endpoints (loans and savings)."""
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from pydantic import BaseModel

from adapters.ports.account_repository import AccountRepository
from adapters.postgres.manual_account_repository import (
    ManualAccountRepository,
    SnapshotAccountRepository,
)
from drivers.dependencies import get_repository, get_sync_user
from drivers.routers.users import connected_user
from entities.account import ManualAccount, ManualAccountRead, UnifiedAccountRead
from entities.user import User
from use_cases.loan_account import CreateLoanAccount, CalculateLoanBalance
from use_cases.savings_import import ImportSavingsFromCSV
from use_cases.account_snapshot import RecordAccountSnapshot, GetNetWorthCharts, GetSnapshotReminder
from use_cases.sync_powens_user import SyncUserData


router = APIRouter(prefix="/accounts")


@router.get("", response_model=list[UnifiedAccountRead])
def accounts_list(
    user: User = Depends(connected_user),
    account_repo: AccountRepository = Depends(get_repository("account")),
    manual_repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
):
    # Fetch data
    bank_accs = account_repo.read(user_id=user.id)
    manual_accs = manual_repo.get_user_accounts(user.id)
    
    unified_list = []

    # Map Bank Accounts
    for acc in bank_accs:
        # Convert to dict and add the discriminator
        acc_data = acc.model_dump()
        acc_data["source_type"] = "bank"
        # Ensure we use 'balance' field (bank accounts have 'balance')
        unified_list.append(acc_data)

    # Map Manual Accounts
    for acc in manual_accs:
        acc_data = acc.model_dump()
        acc_data["source_type"] = "manual"
        # Map 'current_balance' to 'balance' for frontend consistency
        acc_data["balance"] = acc.current_balance 
        unified_list.append(acc_data)

    return unified_list
    

@router.post("/sync")
def accounts_sync(
    user: User = Depends(connected_user),
    sync_user: SyncUserData = Depends(get_sync_user),
):
    sync_user.accounts_sync(user.id)
    return {"status": "sync done"}


@router.post("/{account_id}/sync")
def account_sync(
    user: User = Depends(connected_user),
    account_id: str = "",
    sync_user: SyncUserData = Depends(get_sync_user),
):
    sync_user.account_sync(user.id, account_id)
    return {"status": "sync done"}


class CreateLoanRequest(BaseModel):
    """Request to create a loan account."""
    name: str
    initial_amount: Decimal
    interest_rate: Decimal  # Annual percentage
    duration_months: int
    start_date: date
    icon: str = "CreditCardIcon"
    color: str = "#ef4444"


class CreateSavingsRequest(BaseModel):
    """Request to create a savings account."""
    name: str
    current_balance: Decimal
    icon: str = "PiggyBankIcon"
    color: str = "#10b981"


class RecordSnapshotRequest(BaseModel):
    """Request to record a snapshot."""
    balance: Decimal
    snapshot_date: date | None = None


@router.post("/loans")
def create_loan_account(
    request: CreateLoanRequest,
    user: User = Depends(connected_user),
    repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
) -> ManualAccountRead:
    """
    Create a loan account with automatic monthly balance calculation.
    
    The system will automatically calculate the remaining balance based on:
    - Initial amount
    - Interest rate (annual %)
    - Loan duration (months)
    - Start date
    """
    use_case = CreateLoanAccount(repo)
    account = use_case(
        user_id=user.id,
        name=request.name,
        initial_amount=request.initial_amount,
        interest_rate=request.interest_rate,
        duration_months=request.duration_months,
        start_date=request.start_date,
        icon=request.icon,
        color=request.color,
    )
    return account


@router.post("/savings")
def create_savings_account(
    request: CreateSavingsRequest,
    user: User = Depends(connected_user),
    repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
) -> ManualAccountRead:
    """Create a manual savings account."""
    account = ManualAccount(
        user_id=user.id,
        name=request.name,
        account_type="savings",
        current_balance=request.current_balance,
        currency="EUR",
        icon=request.icon,
        color=request.color,
    )
    return repo.create(account)


@router.post("/savings/import-csv")
async def import_savings_from_csv(
    file: UploadFile = File(...),
    account_name: str = "Imported Savings",
    user: User = Depends(connected_user),
    account_repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
    snapshot_repo: SnapshotAccountRepository = Depends(get_repository("snapshot_account")),
) -> dict:
    """
    Import savings account snapshots from CSV file.
    
    CSV Format (with header):
    date,balance
    2024-01-01,1000.00
    2024-02-01,1100.00
    """
    try:
        content = await file.read()
        csv_content = content.decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read file: {e}")
    
    try:
        use_case = ImportSavingsFromCSV(account_repo, snapshot_repo)
        account, snapshots = use_case(
            user_id=user.id,
            csv_content=csv_content,
            account_name=account_name,
        )
        return {
            "account": account,
            "snapshots_count": len(snapshots),
            "latest_balance": float(account.current_balance),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/manual/{account_id}")
def get_account(
    account_id: str,
    user: User = Depends(connected_user),
    repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
) -> ManualAccountRead:
    """Get a specific account."""
    accounts = repo.read(id=account_id, user_id=user.id)
    if not accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    return accounts[0]


@router.put("/manual/{account_id}")
def update_account(
    account_id: str,
    update_data: dict,
    user: User = Depends(connected_user),
    repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
) -> ManualAccountRead:
    """Update an account."""
    accounts = repo.read(id=account_id, user_id=user.id)
    if not accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    updated = repo.update(account_id, **update_data)
    return updated


@router.delete("/manual/{account_id}")
def delete_account(
    account_id: str,
    user: User = Depends(connected_user),
    repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
) -> dict:
    """Delete an account."""
    accounts = repo.read(id=account_id, user_id=user.id)
    if not accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    repo.delete(account_id)
    return {"message": "Account deleted"}


@router.get("/manual/{account_id}/balance")
def get_loan_balance(
    account_id: str,
    user: User = Depends(connected_user),
    repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
) -> dict:
    """Get current balance for a loan (recalculates automatically)."""
    accounts = repo.read(id=account_id, user_id=user.id)
    if not accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    account = accounts[0]
    if account.account_type != "loan":
        raise HTTPException(status_code=400, detail="Balance calculation only for loans")
    
    use_case = CalculateLoanBalance(repo)
    balance = use_case(account_id)
    return {
        "account_id": str(account_id),
        "current_balance": float(balance),
        "monthly_payment": float(account.loan_monthly_payment or 0),
    }


@router.post("/manual/{account_id}/snapshot")
def record_snapshot(
    account_id: str,
    request: RecordSnapshotRequest,
    user: User = Depends(connected_user),
    account_repo: ManualAccountRepository = Depends(get_repository("manual_accounts")),
    snapshot_repo: SnapshotAccountRepository = Depends(get_repository("snapshot_account")),
) -> dict:
    """Record a snapshot for an account."""
    accounts = account_repo.read(id=account_id, user_id=user.id)
    if not accounts:
        raise HTTPException(status_code=404, detail="Account not found")
    
    use_case = RecordAccountSnapshot(account_repo, snapshot_repo)
    snapshot = use_case(
        manual_account_id=account_id,
        user_id=user.id,
        balance=request.balance,
        snapshot_date=request.snapshot_date
    )
    return {
        "snapshot_id": str(snapshot.id),
        "manual_account_id": str(snapshot.manual_account_id),
        "balance": float(snapshot.balance),
        "snapshot_date": snapshot.snapshot_date.isoformat(),
    }


@router.get("/net-worth/history")
def get_net_worth_history(
    user: User = Depends(connected_user),
    snapshot_repo: SnapshotAccountRepository = Depends(get_repository("snapshot_account")),
) -> dict:
    """Get net worth history for charts."""
    use_case = GetNetWorthCharts(snapshot_repo)
    return use_case(user.id)


@router.get("/snapshot/reminder")
def check_snapshot_reminder() -> dict:
    """Check if today is a snapshot reminder day (first Sunday of month)."""
    use_case = GetSnapshotReminder()
    is_reminder_day = use_case.is_snapshot_day()
    return {
        "is_reminder_day": is_reminder_day,
        "message": "Time for your monthly Net Worth Sunday!" if is_reminder_day else "Not a snapshot day",
    }
