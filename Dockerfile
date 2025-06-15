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
ENV PYTHONPATH=/app/backend

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
    curl \
    postgresql-client \
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
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source code
COPY backend/ ./backend/

# Copy data directory
COPY data/ ./data/

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/build ./backend/frontend/build

# Copy additional files
COPY requirements.txt ./
COPY init_db.sh ./

# Make init script executable
RUN chmod +x init_db.sh

# Set working directory to backend
WORKDIR /app/backend

# Set Python path to include the backend directory
ENV PYTHONPATH=/app/backend:/app

# Create uploads directory with proper permissions
RUN chmod -R 755 uploads/ static/

# Expose port
EXPOSE 5056

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5056/ || exit 1

# Create startup script
COPY <<EOF /app/start.sh
#!/bin/bash
set -e

echo "Waiting for database..."
while ! pg_isready -h db -p 5432 -U postgres; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is up - executing command"

# Initialize database if needed
python3 -c "
import os
import sys
sys.path.append('/app/backend')
try:
    # Import models in dependency order
    import models.user
    import models.league
    import models.football_team
    import models.footballer
    import models.notification
    import models.player
    import models.match
    import models.performance
    import models.physical
    import models.endurance
    import models.conditional
    import models.match_analysis
    
    from utils.database import Database
    from sqlalchemy import create_engine
    from models import Base
    
    # Create database tables
    engine = create_engine(os.getenv('DATABASE_URL'))
    Base.metadata.create_all(engine)
    
    db = Database()
    session = db.connect()
    print('✅ Database connection and tables created successfully')
    session.close()
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

# Start gunicorn
exec gunicorn --bind 0.0.0.0:5056 --workers 2 --timeout 120 --preload app:app
EOF

RUN chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
