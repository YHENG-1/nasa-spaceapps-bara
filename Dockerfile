# ==============================================================================
# Bara: Harmonization of MODIS & VIIRS Hot Spots
# NASA Space Apps Challenge 2026 - Johor Bahru Local Event
# ==============================================================================
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# Install system dependencies (curl for healthchecks, git/build-essential if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements first to leverage Docker layer caching
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code, data cache, and frontend files
COPY backend ./backend
COPY "Bara — MODIS & VIIRS 3D Fire Observatory.html" ./
COPY index.html ./

# Create non-root user for security best practices
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser ${APP_HOME}
USER appuser

# Expose target port
EXPOSE 8000

# Healthcheck to ensure FastAPI API is responsive
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start FastAPI application with Uvicorn
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]
