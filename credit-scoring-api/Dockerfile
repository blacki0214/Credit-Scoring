# Use Python 3.11 slim image (updated from 3.10)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for lightgbm and other packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code and models
COPY app/ ./app/
COPY models/ ./models/

# Local default port (can be overridden at runtime, e.g. PORT=8080 for Cloud Run)
ENV PORT=8000
EXPOSE 8000

# Health check - Use environment variable for port
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Run application with configurable PORT
CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1"]