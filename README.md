# Savibud

[![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)](https://docs.python.org/3/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/tailwindcss-%2338B2AC.svg?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

A modern personal finance management application built with Clean Architecture. Track expenses, manage budgets, set savings goals, and sync with your bank accounts.

## 🌟 Features

- **Bank Account Integration**: Connect with French banks via Powens API
- **Manual Account Management**: Track loans and savings manually
- **Transaction Categorization**: Automatic and manual transaction tagging
- **Budget Planning**: Create monthly budgets with categories
- **Savings Goals**: Set and track savings targets with automation
- **Real-time Sync**: Automatic account balance updates
- **Responsive Design**: Works on desktop and mobile
- **Clean Architecture**: Maintainable and testable codebase

## 🏗️ Architecture

This monorepo follows Clean Architecture principles:

- **Backend (savibud-api)**: FastAPI with Clean Architecture (Entities → Use Cases → Adapters → Drivers)
- **Frontend (savibud-front)**: React with TypeScript and Tailwind CSS
- **Database**: PostgreSQL with Alembic migrations
- **Infrastructure**: Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/savibud.git
   cd savibud
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## � Project Structure

```
savibud/
├── savibud-api/              # FastAPI backend
│   ├── adapters/            # Clean Architecture adapters
│   ├── drivers/             # FastAPI routes & dependencies
│   ├── entities/            # Domain models
│   ├── use_cases/           # Business logic
│   ├── tests/               # Unit & integration tests
│   └── alembic/             # Database migrations
├── savibud-front/           # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   └── utils/           # Utilities
│   └── public/
├── docker-compose.yml       # Production environment
├── docker-compose.dev.yml   # Development environment
└── docs/                    # Documentation
```

## 📚 Documentation

For detailed setup, development, and deployment instructions, see:

- **[Development Guide](docs/DEVELOPMENT.md)** - Complete setup, development workflow, and standards
- **[API Documentation](savibud-api/README.md)** - Backend API details
- **[Frontend Documentation](savibud-front/README.md)** - Frontend specifics

## 🤝 Contributing

1. Read the [Development Guide](docs/DEVELOPMENT.md)
2. Follow TDD principles and Clean Architecture
3. Use conventional commits
4. Ensure tests pass
5. Format code with ruff and ESLint

## 📄 License

[MIT License](LICENSE)

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://reactjs.org/) - JavaScript library for building user interfaces
- [Powens](https://www.powens.com/) - Banking API provider
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html) - Software architecture principles
