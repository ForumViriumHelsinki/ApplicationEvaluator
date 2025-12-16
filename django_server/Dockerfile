# syntax=docker/dockerfile:1

# ============================================================================
# BUILD STAGE - Install dependencies and compile bytecode
# ============================================================================
FROM python:3.11-slim AS builder

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from official image (faster and more secure than curl | sh)
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv

# Set uv environment variables for optimal build
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Install dependencies FIRST (separate layer for better caching)
COPY pyproject.toml ./

# Use cache mount to persist uv's download cache across builds
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project || \
    uv sync --no-dev --no-install-project

# Copy application code
COPY . .

# Install project
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable || \
    uv sync --no-dev --no-editable

# ============================================================================
# RUNTIME STAGE - Minimal production image
# ============================================================================
FROM python:3.11-slim AS runtime

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r django && useradd -r -g django -d /app django

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder --chown=django:django /app/.venv /app/.venv

# Copy application code
COPY --chown=django:django . .

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    PORT=8000

# Make entrypoint executable
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

# Switch to non-root user
USER django

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["gunicorn", "application_evaluator_config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
