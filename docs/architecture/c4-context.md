graph TD
    User((User)) -->|Manages Budget| Savibud[Savibud System]
    Savibud -->|Fetches Data| Powens(Powens API)
    Savibud -->|Stores Data| DB[(Postgres Database)]
    
