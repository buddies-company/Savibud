# --- Base Stage ---
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app


# install build deps then python deps
COPY savibud-api/requirements-lock.txt ./requirements.txt
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && rm -rf /var/lib/apt/lists/* \
    && python -m pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && mkdir -p /app/static/uploads

# copy source
COPY savibud-api/ /app/

# --- API Stage ---
FROM base AS api
EXPOSE 14673
# Run with a single worker by default; increase in production if needed
CMD ["uvicorn", "drivers.main:app", "--host", "0.0.0.0", "--port", "14673", "--workers", "1"]

# --- Scheduler (Worker) Stage ---
FROM base AS scheduler
# We don't expose ports here for security
CMD ["python", "-m", "scheduler.main"]