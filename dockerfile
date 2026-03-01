# =============================================================================
# Multi-Stage Dockerfile for Weather Data Quality Platform
# =============================================================================
# Split multi-stage Dockerfile into two stages: builder and runtime.
# To shorten build times and reduce final image size and speed up deployment, 
# we install dependencies in a separate "builder" stage,
# then copy only the necessary files into a clean "runtime" stage.
# =============================================================================

# ---------------------------------------------------------------------------
# STAGE 1: Builder — install dependencies in a throwaway container
# ---------------------------------------------------------------------------
# slim = 150MB, uses glibc (same as Lambda runtime).
FROM python:3.11-slim AS builder

WORKDIR /build

# WHY copy requirements first, THEN code?
# Docker caches each layer. If requirements.txt hasn't changed, Docker reuses
# the cached pip install layer — saving 30-60 seconds on every build.
# Sample implementation of "layer caching optimization"
COPY requirements.txt requirements-dev.txt ./

RUN pip install --no-cache-dir --user -r requirements-dev.txt

# ---------------------------------------------------------------------------
# STAGE 2: Runtime — lean production image
# ---------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

LABEL maintainer="Andika Bhaskara"
LABEL description="Weather Data Quality Platform - Ingestion & Dashboard"

# by creating non-root user and switching to it, it prevents accidental root execution and enforces best practices.
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

COPY --from=builder /root/.local/lib /usr/local/lib
COPY --from=builder /root/.local/bin /usr/local/bin

# Copy application code
COPY src/ ./src/
COPY dashboard/ ./dashboard/
COPY tests/ ./tests/
COPY weather_dbt/ ./weather_dbt/
COPY .env.example ./.env.example

USER appuser

# Expose Streamlit default port
EXPOSE 8501

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

CMD ["python", "src/ingestion.py"]