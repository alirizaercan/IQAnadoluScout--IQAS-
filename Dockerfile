# Multi-stage Dockerfile for TYFOR project
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source code
COPY frontend/ ./

# Build React app
RUN npm run build

# Stage 2: Python backend with frontend assets
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create necessary directories
RUN mkdir -p backend/static/graphs \
    backend/static/team-logos \
    backend/uploads/videos \
    backend/uploads/processed_videos \
    data/models \
    data/processed_data \
    data/raw_data

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy data directory
COPY data/ ./data/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build ./backend/frontend/build

# Copy additional files
COPY requirements.txt ./
COPY README.md ./

# Set working directory to backend
WORKDIR /app/backend

# Create uploads directory with proper permissions
RUN chmod -R 755 uploads/ static/

# Expose port
EXPOSE 5056

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5056/ || exit 1

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5056", "--workers", "4", "--timeout", "120", "app:app"]
