#!/bin/bash

# Deploy to Staging Script
echo "🚀 Starting deployment to staging..."

# Set environment variables
export ENVIRONMENT=staging
export DATABASE_URL=postgresql://postgres:190123@staging-db:5432/myapp
export SECRET_KEY=staging-secret-key-$(date +%s)

# Build Docker image
echo "📦 Building Docker image..."
docker build -t myapp-backend:staging .

# Tag for staging
docker tag myapp-backend:staging myapp-backend:latest

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.staging.yml down

# Start new containers
echo "🏃 Starting new containers..."
docker-compose -f docker-compose.staging.yml up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Wait for database to be fully ready
echo "⏳ Waiting for database to be fully ready..."
sleep 15

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose -f docker-compose.staging.yml exec app python -c "
import time
from sqlalchemy import create_engine, text
from app.core.config import DB_URL

# Wait for database connection
max_retries = 30
for i in range(max_retries):
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('✅ Database connection successful')
        break
    except Exception as e:
        print(f'⏳ Waiting for database... ({i+1}/{max_retries})')
        time.sleep(2)
else:
    print('❌ Database connection failed after 60 seconds')
    exit(1)

# Create tables
from app.db.database import engine
from app.model import user, feature, rbac, abac
from app.db import Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created/updated')
"

# Health check
echo "🏥 Running health check..."
sleep 5
 PORT=${PORT:-8000}
curl -f http://localhost:$PORT/health || echo "❌ Health check failed"

echo "✅ Deployment to staging completed!"
echo "🌐 Backend API: http://localhost:$PORT"
echo "📚 API Docs: http://localhost:$PORT/docs"
    