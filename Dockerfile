FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY src/ ./src/
COPY model/ ./model/
COPY data/ ./data/

# Health check using your actual predict function
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from src.predict import load_model; print('OK')" || exit 1

EXPOSE 8000

# Simple command to keep container running and test model
CMD ["python", "-c", "from src.predict import load_model; print('Sentiment Analysis Model Ready'); import time; time.sleep(3600)"]