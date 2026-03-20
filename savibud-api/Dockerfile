# --- Base Stage ---
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY savibud-api/pyproject.toml savibud-api/uv.lock ./

# Install Python dependencies with uv
RUN uv sync --frozen --no-install-project --no-dev

# Copy source code
COPY savibud-api/ /app/

# Install the project itself
RUN uv sync --frozen --no-dev

# Create uploads directory
RUN mkdir -p /app/static/uploads

# --- API Stage ---
FROM base AS api
EXPOSE 14673
# Run with a single worker by default; increase in production if needed
CMD ["uv", "run", "uvicorn", "drivers.main:app", "--host", "0.0.0.0", "--port", "14673", "--workers", "1"]

# --- Scheduler (Worker) Stage ---
FROM base AS scheduler
# We don't expose ports here for security
CMD ["uv", "run", "python", "-m", "scheduler.main"]