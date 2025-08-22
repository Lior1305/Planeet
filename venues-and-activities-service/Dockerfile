FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Copy MongoDB initialization script (this will be used by the MongoDB container, not this service)
# Note: This is actually not needed in the venues service Dockerfile since MongoDB runs separately
# The init.js should be mounted to the MongoDB container in the k8s deployment

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
