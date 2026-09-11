# Production Dockerfile for School Lost & Found Management System
# Compatible with Google Cloud Run (Firebase Hosting rewrite) & Render Docker Runtime

FROM python:3.10-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV HOST=0.0.0.0
ENV DB_MODE=auto

# Working directory inside container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Initialize fallback database and pre-seed records
RUN python init_db.py

# Expose port (Cloud Run & Render pass $PORT dynamically)
EXPOSE 8080

# Run with Gunicorn WSGI server
CMD exec gunicorn --bind :$PORT --workers 2 --threads 4 --timeout 120 app:app
