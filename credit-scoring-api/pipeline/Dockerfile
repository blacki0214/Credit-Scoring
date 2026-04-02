FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy pipeline code
COPY feature_engineering.py .
COPY retrain_job.py .
COPY email_notifier.py .

# Set environment variables (can be overridden at runtime)
ENV GCS_BUCKET=credit-scoring-retrain-513943636250
ENV MIN_SAMPLES=500
ENV MIN_AUC_IMPROVEMENT=0.02
ENV PROMOTION_THRESHOLD=0.86

# Run the retraining job
CMD ["python", "retrain_job.py"]
