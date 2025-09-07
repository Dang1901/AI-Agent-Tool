#!/usr/bin/env python3
"""
Run staging environment without Docker
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def run_staging():
    """Run staging environment directly with Python"""
    print("🚀 Starting staging environment...")
    
    # Set environment variables
    os.environ["DATABASE_URL"] = "postgresql://postgres:190123@localhost:5432/myapp"
    os.environ["SECRET_KEY"] = "staging-secret-key"
    os.environ["ENVIRONMENT"] = "staging"
    
    print("✅ Environment variables set")
    print(f"📊 Database URL: {os.environ['DATABASE_URL']}")
    
    # Check if PostgreSQL is running
    print("🔍 Checking PostgreSQL connection...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="myapp",
            user="postgres",
            password="190123"
        )
        conn.close()
        print("✅ PostgreSQL connection successful")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("Please make sure PostgreSQL is running on localhost:5432")
        return False
    
    # Install dependencies
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # Create database tables
    print("🗄️ Creating database tables...")
    try:
        from app.db.database import engine
        from app.model import user, feature, rbac, abac
        from app.db import Base
        
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/updated")
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False
    
    # Get port from environment or default to 8000
    port = os.getenv("PORT", "8000")
    
    # Start the server
    print("🏃 Starting FastAPI server...")
    print(f"🌐 Backend API: http://localhost:{port}")
    print(f"📚 API Docs: http://localhost:{port}/docs")
    print(f"🏥 Health Check: http://localhost:{port}/health")
    print("\nPress Ctrl+C to stop the server")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", port,
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        return True
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

if __name__ == "__main__":
    success = run_staging()
    if not success:
        sys.exit(1)
