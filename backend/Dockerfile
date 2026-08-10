FROM python:3.11-slim

# Prevent Python from writing .pyc files & enable unbuffered stdout/stderr logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/backend

# Install OS dependencies required by OpenCV, EasyOCR, and PyTorch
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker layer caching
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/backend/requirements.txt

# Copy root yolo11n.pt model if present
COPY backend/yolo11n.pt* /app/backend/

# Copy backend application source code
COPY backend /app/backend

# Copy root models directory if present
COPY models /app/models

# Create required persistent directories with appropriate permissions
RUN mkdir -p /app/backend/uploads /app/models /app/logs && \
    chmod +x /app/backend/entrypoint.sh

WORKDIR /app/backend

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/api/system/health || exit 1

ENTRYPOINT ["/app/backend/entrypoint.sh"]
