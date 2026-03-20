# Development Guide

Welcome! This document covers the setup and standards for the Savibud monorepo.

## Overview

Savibud is a personal finance management application built as a monorepo with a FastAPI backend and a React frontend. The project follows Clean Architecture principles and Test-Driven Development (TDD) practices.

## Tech Stack

### Backend (savibud-api)
- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Package Management**: uv
- **Database**: PostgreSQL
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Migration Tool**: Alembic
- **Architecture**: Clean Architecture (Entities, Use Cases, Adapters, Drivers)
- **Testing**: pytest
- **Linting**: ruff

### Frontend (savibud-front)
- **Framework**: React 18
- **Build Tool**: Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React hooks + Context
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Version Control**: Git with Conventional Commits

## Prerequisites

Before starting development, ensure you have the following installed:

- **Python 3.11+**: [Download from python.org](https://python.org)
- **Node.js 18+**: [Download from nodejs.org](https://nodejs.org)
- **uv**: Python package manager (`pip install uv`)
- **Docker & Docker Compose**: [Install Docker](https://docs.docker.com/get-docker/)
- **Git**: Version control system

## Project Structure

```
savibud/
├── savibud-api/          # FastAPI backend
│   ├── adapters/         # Clean Architecture adapters layer
│   ├── drivers/          # Clean Architecture drivers layer
│   ├── entities/         # Domain entities
│   ├── use_cases/        # Business logic
│   ├── tests/            # Unit and integration tests
│   └── alembic/          # Database migrations
├── savibud-front/        # React frontend
│   ├── src/
│   ├── public/
│   └── dist/
├── docker-compose.yml    # Development environment
└── docs/                 # Documentation
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/buddies-company/Savibud.git
cd savibud
```

### 2. Backend Setup

```bash
cd savibud-api

# Install dependencies with uv
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the development server
uv run fastapi dev main.py
```

### 3. Frontend Setup

```bash
cd ../savibud-front

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 4. Full Stack with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

## Running the Application

### Development Mode

```bash
# Backend
cd savibud-api && uv run fastapi dev main.py

# Frontend (in another terminal)
cd savibud-front && npm run dev
```

### Production Mode

```bash
# Build and run with Docker
docker-compose -f docker-compose.prod.yml up -d
```

## Development Workflow

### Clean Architecture Guidelines

Always follow Clean Architecture principles:

- **Entities** (`entities/`): Core business objects
- **Use Cases** (`use_cases/`): Application business rules
- **Adapters** (`adapters/`): Interface adapters (repositories, external APIs)
- **Drivers** (`drivers/`): Framework & delivery mechanisms (FastAPI routes, CLI)

**Dependency Rule**: Inner layers (entities) should never depend on outer layers (adapters/drivers).

### Test-Driven Development (TDD)

1. Write failing tests first
2. Write minimal code to pass tests
3. Refactor while maintaining test coverage

```bash
# Run backend tests
cd savibud-api
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Code Quality

```bash
# Lint and format backend
uv run ruff check .
uv run ruff format .

# Lint frontend
cd savibud-front
npm run lint
npm run format
```

### Commit Messages

Follow Conventional Commits specification:

```bash
feat: add user authentication
fix: resolve transaction import bug
docs: update API documentation
refactor: simplify account repository
test: add unit tests for savings goals
```

## Testing

### Backend Testing

```bash
# Unit tests
uv run pytest tests/unit/

# Integration tests
uv run pytest tests/integration/

# All tests with coverage
uv run pytest --cov=. --cov-report=term-missing
```

### Frontend Testing

```bash
cd savibud-front
npm test
```

## API Documentation

When the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Database Management

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Database Reset

```bash
# Stop containers
docker-compose down

# Remove volumes
docker volume rm savibud_postgres_data

# Restart
docker-compose up -d
```

## Deployment

### Staging

```bash
# Deploy to staging
git push origin develop
# CI/CD pipeline handles deployment
```

### Production

```bash
# Tag release
git tag v1.0.0
git push origin main

# CI/CD pipeline handles production deployment
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Follow TDD: write tests first
4. Ensure all tests pass: `uv run pytest`
5. Format code: `uv run ruff format .`
6. Commit with conventional commits
7. Push and create pull request

### Pull Request Guidelines

- Include tests for new features
- Update documentation if needed
- Ensure CI passes
- Get code review approval

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check Python version: `python --version`
- Ensure virtual environment is activated
- Verify database connection in `.env`

**Frontend build fails:**
- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version`

**Database connection issues:**
- Ensure PostgreSQL is running: `docker-compose ps`
- Check connection string in `.env`

**Tests failing:**
- Run specific test: `uv run pytest tests/unit/test_specific.py`
- Check test database configuration

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Conventional Commits](https://conventionalcommits.org/)
- [uv Documentation](https://github.com/astral-sh/uv)
