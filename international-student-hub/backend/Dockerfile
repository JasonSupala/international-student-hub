# =============================================================================
# Dockerfile — Django Backend
# Multi-stage build: keeps the final image lean by separating build dependencies
# =============================================================================

# Use Python 3.12 slim (smaller than full image, no unnecessary system packages)
FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files to disk (keeps container clean)
ENV PYTHONDONTWRITEBYTECODE=1
# Prevent Python from buffering stdout/stderr (logs appear in real time)
ENV PYTHONUNBUFFERED=1

# Set working directory inside the container
WORKDIR /app

# --------------------------------------------------------------------------
# System dependencies
# --------------------------------------------------------------------------
# psycopg2-binary needs libpq; Pillow needs libjpeg + zlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# --------------------------------------------------------------------------
# Python dependencies
# --------------------------------------------------------------------------
# Copy only requirements first to leverage Docker layer caching.
# If requirements.txt hasn't changed, this layer is reused on rebuild.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# --------------------------------------------------------------------------
# Application code
# --------------------------------------------------------------------------
COPY . .

# --------------------------------------------------------------------------
# Entrypoint script
# --------------------------------------------------------------------------
# The entrypoint handles migrations and then starts the server.
# This is separated from the Dockerfile CMD so it's easy to override
# in docker-compose (e.g., run a Celery worker instead of gunicorn).
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
