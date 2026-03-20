# C4 Code Diagram

## Code Level Overview

This diagram shows key classes and their relationships within the system.

```mermaid
classDiagram

    %% Relationships
    User ||--o{ Account : owns
    User ||--o{ Transaction : owns
    User ||--o{ Category : owns
    User ||--o{ SavingsGoal : owns

    Account ||--o{ Transaction : contains

    Category ||--o{ Transaction : categorizes

    SavingsGoal ||--o{ Transaction : funds

    %% Backend Classes
    class User {
        +id: UUID
        +email: str
        +created_at: datetime
        +is_active(): bool
    }

    class Account {
        +id: UUID
        +user_id: UUID
        +powens_account_id: str
        +name: str
        +balance: Decimal
        +currency: str
    }

    class Transaction {
        +id: UUID
        +user_id: UUID
        +account_id: UUID
        +category_id: UUID
        +date: date
        +label: str
        +amount: Decimal
        +powens_transaction_id: str
    }

    class Category {
        +id: UUID
        +user_id: UUID
        +name: str
        +budget_amount: Decimal
        +budget_period: str
        +is_income: bool
    }

    class SavingsGoal {
        +id: UUID
        +user_id: UUID
        +name: str
        +target_amount: Decimal
        +current_amount: Decimal
        +automation_amount: Decimal
        +automation_frequency: str
    }

    %% Frontend Classes/Types
    class UserContext {
        +user: User | null
        +login(email, password): Promise<void>
        +logout(): void
    }

    class AccountService {
        +getAccounts(): Promise<Account[]>
        +syncAccount(accountId): Promise<void>
    }

    class TransactionService {
        +getTransactions(filters): Promise<Transaction[]>
        +categorizeTransaction(id, categoryId): Promise<void>
    }

    class BudgetService {
        +getBudgets(): Promise<Category[]>
        +createBudget(budget): Promise<Category>
    }

    class SavingsService {
        +getGoals(): Promise<SavingsGoal[]>
        +updateGoal(id, updates): Promise<SavingsGoal>
    }

    %% Frontend Services
    UserContext ..> AccountService : uses
    UserContext ..> TransactionService : uses
    UserContext ..> BudgetService : uses
    UserContext ..> SavingsService : uses

    %% Styling
    classDef backend fill:#e1f5fe,stroke:#01579b
    classDef frontend fill:#f3e5f5,stroke:#4a148c
    classDef entity fill:#c8e6c9,stroke:#1b5e20

    class User,Account,Transaction,Category,SavingsGoal backend
    class UserContext,AccountService,TransactionService,BudgetService,SavingsService frontend
```

## Key Classes

### Backend Domain Entities

- **User**: Represents application users with authentication
- **Account**: Bank accounts linked via Powens API
- **Transaction**: Individual financial transactions
- **Category**: Budget categories with spending limits
- **SavingsGoal**: Savings targets with automation

### Frontend Services

- **UserContext**: React context for authentication state
- **AccountService**: API client for account operations
- **TransactionService**: API client for transaction management
- **BudgetService**: API client for budget operations
- **SavingsService**: API client for savings goals

## Design Patterns

### Backend Patterns

- **Repository Pattern**: Data access abstraction
- **Use Case Pattern**: Business logic encapsulation
- **Dependency Injection**: Loose coupling between layers
- **Factory Pattern**: Object creation for external services

### Frontend Patterns

- **Context Pattern**: Global state management
- **Service Layer**: API abstraction
- **Component Composition**: Reusable UI components
- **Custom Hooks**: Logic extraction from components

## Data Flow

1. **User Action** → React Component
2. **Component** → Service Method
3. **Service** → HTTP Request to FastAPI
4. **FastAPI Route** → Use Case
5. **Use Case** → Repository
6. **Repository** → Database Query
7. **Response** flows back through the layers

## Type Safety

- **Backend**: Pydantic models for request/response validation
- **Frontend**: TypeScript interfaces for type safety
- **API Contract**: OpenAPI schema ensures consistency