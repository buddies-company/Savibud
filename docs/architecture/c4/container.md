# C4 Container Diagram

## Container Overview

This diagram shows the high-level technology choices and how containers communicate.

```mermaid
graph TB
    subgraph "User Devices"
        Browser[Web Browser<br/>Chrome, Firefox, Safari]
    end

    subgraph "Savibud System"
        subgraph "Frontend Container"
            ReactApp[React Application<br/>TypeScript + Vite<br/>Port: 3000<br/>Serves SPA]
        end

        subgraph "Backend Container"
            FastAPI[FastAPI Application<br/>Python + Uvicorn<br/>Port: 8000<br/>REST API]
        end

        subgraph "Database Container"
            Postgres[(PostgreSQL Database<br/>Port: 5432<br/>Stores all data)]
        end

        subgraph "External Services"
            PowensAPI[Powens Banking API<br/>External service<br/>Bank data provider]
        end
    end

    Browser -->|HTTPS| ReactApp
    ReactApp -->|HTTPS/REST| FastAPI
    FastAPI -->|JDBC| Postgres
    FastAPI -->|HTTPS| PowensAPI

    style Browser fill:#e3f2fd
    style ReactApp fill:#c8e6c9
    style FastAPI fill:#fff3e0
    style Postgres fill:#fce4ec
    style PowensAPI fill:#f3e5f5
```

## Container Descriptions

### React Application (Frontend)
- **Technology**: React 18, TypeScript, Vite, Tailwind CSS
- **Purpose**: Provides the user interface for managing personal finances
- **Responsibilities**:
  - Display account balances and transactions
  - Allow budget creation and monitoring
  - Enable savings goal management
  - Handle user authentication

### FastAPI Application (Backend)
- **Technology**: FastAPI, Python 3.11, SQLModel, Alembic
- **Purpose**: Implements business logic and data persistence
- **Responsibilities**:
  - User authentication and authorization
  - Account and transaction management
  - Budget and savings goal logic
  - Powens API integration
  - Database operations

### PostgreSQL Database
- **Technology**: PostgreSQL 15+
- **Purpose**: Persistent storage for all application data
- **Responsibilities**:
  - Store user accounts and profiles
  - Maintain transaction history
  - Track budgets and categories
  - Store savings goals and progress

### Powens Banking API
- **Technology**: External REST API
- **Purpose**: Provides access to French banking institutions
- **Responsibilities**:
  - Account balance synchronization
  - Transaction history retrieval
  - Real-time financial data updates

## Technology Decisions

- **Frontend**: React for component reusability, TypeScript for type safety
- **Backend**: FastAPI for high performance, Python for rapid development
- **Database**: PostgreSQL for ACID compliance and complex queries
- **Styling**: Tailwind CSS for utility-first approach
- **Build Tool**: Vite for fast development and optimized production builds