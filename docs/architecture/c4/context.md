# C4 Context Diagram

## System Context

This diagram shows Savibud in relation to its users and external systems.

```mermaid
graph TD
    subgraph "External Systems"
        Powens[Powens Banking API<br/>Provides bank account data<br/>and transaction history]
    end

    subgraph "Savibud System"
        WebApp[Web Application<br/>React + TypeScript<br/>User Interface]
        API[API Application<br/>FastAPI + Python<br/>Business Logic & Data Access]
        DB[(PostgreSQL Database<br/>Stores user data,<br/>transactions, budgets)]
    end

    User((Personal Finance User)) -->|Manages finances via| WebApp
    WebApp -->|Makes API calls to| API
    API -->|Fetches bank data from| Powens
    API -->|Reads/Writes data to| DB

    style User fill:#e1f5fe
    style WebApp fill:#c8e6c9
    style API fill:#fff3e0
    style DB fill:#fce4ec
    style Powens fill:#f3e5f5
```

## Key Relationships

- **User**: Individuals managing their personal finances
- **Web Application**: Frontend interface for user interaction
- **API Application**: Backend providing business logic and data management
- **Powens API**: External banking service for account synchronization
- **Database**: Persistent storage for all application data

## Quality Attributes

- **Usability**: Intuitive interface for non-technical users
- **Performance**: Fast response times for financial data
- **Security**: Secure handling of financial information
- **Reliability**: Consistent data synchronization
- **Scalability**: Support for growing user base
