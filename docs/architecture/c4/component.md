# C4 Component Diagram

## Component Overview

This diagram shows the key components within each container and their interactions.

```mermaid
graph TB
    subgraph "React Application"
        Router[React Router<br/>Client-side routing]
        AuthProvider[Auth Context<br/>Authentication state]
        Dashboard[Dashboard Component<br/>Financial overview]
        Accounts[Accounts Component<br/>Account management]
        Transactions[Transactions Component<br/>Transaction listing]
        Budgets[Budgets Component<br/>Budget planning]
        Savings[Savings Component<br/>Goals tracking]
        APIClient[API Client<br/>HTTP requests]
    end

    subgraph "FastAPI Application"
        AuthMiddleware[Auth Middleware<br/>JWT validation]
        UserRoutes[User Routes<br/>Authentication endpoints]
        AccountRoutes[Account Routes<br/>Account management]
        TransactionRoutes[Transaction Routes<br/>Transaction operations]
        BudgetRoutes[Budget Routes<br/>Budget management]
        SavingsRoutes[Savings Routes<br/>Goals management]

        AuthUseCase[Auth Use Case<br/>Login/logout logic]
        AccountUseCase[Account Use Case<br/>Account operations]
        TransactionUseCase[Transaction Use Case<br/>Transaction processing]
        BudgetUseCase[Budget Use Case<br/>Budget calculations]
        SavingsUseCase[Savings Use Case<br/>Goal tracking]

        AccountRepo[Account Repository<br/>Account data access]
        TransactionRepo[Transaction Repository<br/>Transaction data access]
        BudgetRepo[Budget Repository<br/>Budget data access]
        SavingsRepo[Savings Repository<br/>Goals data access]
        UserRepo[User Repository<br/>User data access]

        PowensAdapter[Powens Adapter<br/>Bank API integration]
    end

    subgraph "PostgreSQL Database"
        Users[users table]
        Accounts[accounts table]
        Transactions[transactions table]
        Categories[categories table]
        SavingsGoals[savings_goals table]
    end

    Router --> Dashboard
    Router --> Accounts
    Router --> Transactions
    Router --> Budgets
    Router --> Savings

    Dashboard --> APIClient
    Accounts --> APIClient
    Transactions --> APIClient
    Budgets --> APIClient
    Savings --> APIClient

    APIClient -->|HTTPS| AuthMiddleware
    AuthMiddleware --> UserRoutes
    AuthMiddleware --> AccountRoutes
    AuthMiddleware --> TransactionRoutes
    AuthMiddleware --> BudgetRoutes
    AuthMiddleware --> SavingsRoutes

    UserRoutes --> AuthUseCase
    AccountRoutes --> AccountUseCase
    TransactionRoutes --> TransactionUseCase
    BudgetRoutes --> BudgetUseCase
    SavingsRoutes --> SavingsUseCase

    AuthUseCase --> UserRepo
    AccountUseCase --> AccountRepo
    TransactionUseCase --> TransactionRepo
    BudgetUseCase --> BudgetRepo
    SavingsUseCase --> SavingsRepo

    AccountUseCase --> PowensAdapter
    TransactionUseCase --> PowensAdapter

    UserRepo --> Users
    AccountRepo --> Accounts
    TransactionRepo --> Transactions
    BudgetRepo --> Categories
    SavingsRepo --> SavingsGoals

    style Router fill:#e8f5e8
    style AuthProvider fill:#e8f5e8
    style Dashboard fill:#e8f5e8
    style Accounts fill:#e8f5e8
    style Transactions fill:#e8f5e8
    style Budgets fill:#e8f5e8
    style Savings fill:#e8f5e8
    style APIClient fill:#e8f5e8

    style AuthMiddleware fill:#fff2cc
    style UserRoutes fill:#fff2cc
    style AccountRoutes fill:#fff2cc
    style TransactionRoutes fill:#fff2cc
    style BudgetRoutes fill:#fff2cc
    style SavingsRoutes fill:#fff2cc

    style AuthUseCase fill:#d5e8d4
    style AccountUseCase fill:#d5e8d4
    style TransactionUseCase fill:#d5e8d4
    style BudgetUseCase fill:#d5e8d4
    style SavingsUseCase fill:#d5e8d4

    style AccountRepo fill:#b3e5fc
    style TransactionRepo fill:#b3e5fc
    style BudgetRepo fill:#b3e5fc
    style SavingsRepo fill:#b3e5fc
    style UserRepo fill:#b3e5fc

    style PowensAdapter fill:#f8cecc

    style Users fill:#f5f5f5
    style Accounts fill:#f5f5f5
    style Transactions fill:#f5f5f5
    style Categories fill:#f5f5f5
    style SavingsGoals fill:#f5f5f5
```

## Component Descriptions

### Frontend Components

- **React Router**: Handles client-side navigation
- **Auth Context**: Manages authentication state across the app
- **Dashboard**: Main financial overview page
- **Accounts**: Account listing and management
- **Transactions**: Transaction history and categorization
- **Budgets**: Budget creation and monitoring
- **Savings**: Savings goals tracking
- **API Client**: Axios-based HTTP client for backend communication

### Backend Components

#### Routes (Controllers)
- **Auth Middleware**: JWT token validation
- **User/Account/Transaction/Budget/Savings Routes**: REST API endpoints

#### Use Cases (Business Logic)
- **Auth/Account/Transaction/Budget/Savings Use Cases**: Application business rules

#### Repositories (Data Access)
- **User/Account/Transaction/Budget/Savings Repositories**: Database abstraction layer

#### Adapters
- **Powens Adapter**: Integration with external banking API

### Database Tables

- **users**: User accounts and authentication
- **accounts**: Bank account information
- **transactions**: Financial transactions
- **categories**: Budget categories
- **savings_goals**: Savings targets and progress

## Clean Architecture Layers

The backend follows Clean Architecture principles:

1. **Entities** (Core business objects)
2. **Use Cases** (Application business rules)
3. **Interface Adapters** (Controllers, Repositories, External APIs)
4. **Frameworks & Drivers** (FastAPI, Database connections)