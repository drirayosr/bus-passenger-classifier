# Bus Passenger Classification API - Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements folder
COPY requirements/ ./requirements/

# Install Python dependencies (production: base + mlflow + api)
RUN pip install --no-cache-dir -r requirements/base.txt \
    && pip install --no-cache-dir -r requirements/mlflow.txt \
    && pip install --no-cache-dir -r requirements/api.txt

# Copy application code
COPY config/ ./config/
COPY src/ ./src/
COPY api/ ./api/
COPY models/ ./models/
COPY mlruns/ ./mlruns/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Set environment variable to use local model
ENV USE_LOCAL_MODEL=true
ENV LOCAL_MODEL_PATH=/app/models/pipeline.joblib

# Run the API
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
