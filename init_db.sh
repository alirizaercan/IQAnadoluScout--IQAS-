#!/bin/bash
# Database initialization script

set -e

echo "🔄 Starting database initialization..."

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
python3 -c "
import time
import psycopg2
import os

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        conn.close()
        print('✅ Database connection successful!')
        break
    except psycopg2.OperationalError:
        retry_count += 1
        print(f'⏳ Database not ready, retrying... ({retry_count}/{max_retries})')
        time.sleep(2)
else:
    print('❌ Could not connect to database after 30 retries')
    exit(1)
"

echo "🔧 Initializing SQLAlchemy models..."
python3 -c "
import sys
sys.path.append('/app/backend')

try:
    from utils.database import Database
    from sqlalchemy import text
    
    # Import models in dependency order to avoid foreign key issues
    # First: Base tables without foreign keys
    import models.user
    import models.league  
    import models.football_team
    
    # Second: Tables with foreign keys to base tables
    import models.footballer
    import models.notification
    
    # Third: Tables with foreign keys to footballer/team
    import models.player
    import models.match
    import models.performance
    import models.physical
    import models.endurance
    import models.conditional
    import models.match_analysis
    
    print('✅ All models imported successfully')
    
    # Create database tables
    db = Database()
    session = db.connect()
    
    # Create all tables in the correct order
    from models import Base
    from sqlalchemy import create_engine
    import os
    
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    # Drop all tables if they exist (for clean slate)
    print('🗑️ Dropping existing tables...')
    Base.metadata.drop_all(engine)
    
    # Create all tables fresh
    print('🏗️ Creating database tables...')
    Base.metadata.create_all(engine)
    
    print('✅ Database tables created successfully')
    
    session.close()
    
except Exception as e:
    print(f'❌ Database initialization failed: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

echo "✅ Database initialization completed!"
