###############################################
# Stage 1: Builder & Test Runner
###############################################
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies in a virtual env for cleaner layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Run linting & tests during build (fail-fast)
# Uncomment the line below once tests are confirmed working:
# RUN python -m pytest --tb=short -q || exit 1

###############################################
# Stage 2: Production Image
###############################################
FROM python:3.11-slim AS production

# Security: create a non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --from=builder /app /app

# Security: switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check inside the container
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

# Run with production server (Uvicorn) with multiple workers for concurrency
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
