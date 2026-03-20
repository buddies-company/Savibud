# Savibud API

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://docs.python.org/3/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![OpenAPI](https://img.shields.io/badge/openapi-6BA539?style=for-the-badge&logo=openapi-initiative&logoColor=fff)](https://www.openapis.org/)
[![Swagger](https://img.shields.io/badge/-Swagger-%23Clojure?style=for-the-badge&logo=swagger&logoColor=white)](https://swagger.io/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg?style=for-the-badge)](https://github.com/astral-sh/ruff)
[![Typed with: pydantic](https://img.shields.io/badge/typed%20with-pydantic-BA600F.svg?style=for-the-badge)](https://docs.pydantic.dev/)

## Overview

Savibud API is the backend service for Savibud, a personal finance management application. Built with FastAPI and following Clean Architecture principles, it provides RESTful endpoints for managing accounts, transactions, budgets, and savings goals.

## Features

- **Account Management**: Handle bank accounts and manual accounts (loans/savings)
- **Transaction Tracking**: Import and categorize financial transactions
- **Budgeting**: Create and manage budgets with categories
- **Savings Goals**: Set and track savings targets with automation
- **Powens Integration**: Connect with French banking APIs
- **Real-time Sync**: Automatic account synchronization
- **Clean Architecture**: Maintainable and testable codebase

## Tech Stack

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Migrations**: Alembic
- **Package Manager**: uv
- **Linting/Formatting**: ruff
- **Testing**: pytest
- **Containerization**: Docker

## Architecture

We use Clean Architecture to maintain clear distinction between business logic and implementation details.

### Layers

- **Entities**: Core business objects (Account, Transaction, etc.)
- **Use Cases**: Application business rules
- **Adapters**: Interface adapters (repositories, external APIs)
- **Drivers**: Framework & delivery mechanisms (FastAPI routes, CLI)

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL
- uv (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/buddies-company/Savibud.git
   cd savibud/savibud-api
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database URL and other settings
   ```

4. **Run database migrations**
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the development server**
   ```bash
   uv run fastapi dev main.py
   ```

The API will be available at `http://localhost:8000`.

## Usage

### API Documentation

When running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Key Endpoints

- `GET /accounts` - List user accounts
- `POST /accounts/sync` - Sync account data
- `GET /transactions` - Get transactions
- `POST /categories` - Create budget category
- `GET /savings-goals` - List savings goals

## Development

### Code Quality

```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check . --fix
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html
```

### Database Management

```bash
# Create migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

## Docker

### Development

```bash
docker-compose up -d
```

### Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Configuration

Environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `POWENS_CLIENT_ID`: Powens API client ID
- `POWENS_CLIENT_SECRET`: Powens API client secret

## Contributing

1. Follow Clean Architecture principles
2. Write tests first (TDD)
3. Use conventional commits
4. Ensure all tests pass
5. Format code with ruff

## License

[MIT License](LICENSE)

## Support

For questions or issues, please open a GitHub issue.
