from datetime import date
from decimal import Decimal
from uuid import UUID

from adapters.ports.account_repository import ManualAccountRepository
from entities.account import ManualAccount


class CreateLoanAccount:
    """Use case to create a loan account with automatic monthly balance calculation."""

    def __init__(self, repo: ManualAccountRepository):
        self.repo = repo

    def __call__(
        self,
        user_id: UUID,
        name: str,
        initial_amount: Decimal,
        interest_rate: Decimal,
        duration_months: int,
        start_date: date,
        icon: str = "CreditCardIcon",
        color: str = "#ef4444",
    ) -> ManualAccount:
        """
        Create a loan account.
        
        Args:
            user_id: User ID
            name: Loan name (e.g., "Home Mortgage")
            initial_amount: Initial loan amount
            interest_rate: Annual interest rate as percentage (e.g., 3.5 for 3.5%)
            duration_months: Total loan duration in months
            start_date: Loan start date
            icon: Icon name (default: CreditCardIcon)
            color: Hex color code (default: red)
        
        Returns:
            Created ManualAccount
        """
        # Calculate monthly payment using PMT formula
        # PMT = P * [r(1+r)^n] / [(1+r)^n-1]
        monthly_rate = float(interest_rate) / 100 / 12
        n = duration_months
        P = float(initial_amount)
        
        if monthly_rate == 0:
            monthly_payment = P / n
        else:
            numerator = monthly_rate * ((1 + monthly_rate) ** n)
            denominator = ((1 + monthly_rate) ** n) - 1
            monthly_payment = P * (numerator / denominator)
        
        # Create the account
        account = ManualAccount(
            user_id=user_id,
            name=name,
            account_type="loan",
            current_balance=initial_amount,
            currency="EUR",
            loan_initial_amount=initial_amount,
            loan_interest_rate=interest_rate,
            loan_duration_months=duration_months,
            loan_start_date=start_date,
            loan_monthly_payment=Decimal(str(round(monthly_payment, 2))),
            icon=icon,
            color=color,
        )
        
        return self.repo.create(account)


class CalculateLoanBalance:
    """Use case to calculate current loan balance based on time elapsed."""

    def __init__(self, repo: ManualAccountRepository):
        self.repo = repo

    def __call__(self, account_id: UUID) -> Decimal:
        """Calculate and return the current balance of a loan."""
        accounts = self.repo.read(id=account_id)
        if not accounts:
            raise ValueError(f"Account {account_id} not found")
        
        account = accounts[0]
        balance = self.repo.calculate_loan_balance(account)
        
        # Update the current_balance
        account.current_balance = Decimal(str(round(balance, 2)))
        account.updated_at = __import__("datetime").datetime.utcnow()
        self.repo.update(account.id, current_balance=account.current_balance)
        
        return account.current_balance
