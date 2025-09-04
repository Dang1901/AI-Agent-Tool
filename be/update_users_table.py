#!/usr/bin/env python3
"""
Script to update users table structure to match the new model
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.core.config import DB_URL

def update_users_table():
    """Update users table structure to match new model"""
    print("🔄 Updating users table structure...")
    
    try:
        # Create engine
        engine = create_engine(DB_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check current table structure
        print("📋 Checking current table structure...")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """))
        
        existing_columns = [row[0] for row in result.fetchall()]
        print(f"Current columns: {existing_columns}")
        
        # Add missing columns
        print("\n🏗️ Adding missing columns...")
        
        # Add is_active column if not exists
        if 'is_active' not in existing_columns:
            print("Adding is_active column...")
            db.execute(text("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE"))
        
        # Add is_verified column if not exists
        if 'is_verified' not in existing_columns:
            print("Adding is_verified column...")
            db.execute(text("ALTER TABLE users ADD COLUMN is_verified BOOLEAN DEFAULT FALSE"))
        
        # Add department column if not exists
        if 'department' not in existing_columns:
            print("Adding department column...")
            db.execute(text("ALTER TABLE users ADD COLUMN department VARCHAR(100)"))
        
        # Add position column if not exists
        if 'position' not in existing_columns:
            print("Adding position column...")
            db.execute(text("ALTER TABLE users ADD COLUMN position VARCHAR(100)"))
        
        # Add clearance_level column if not exists
        if 'clearance_level' not in existing_columns:
            print("Adding clearance_level column...")
            db.execute(text("ALTER TABLE users ADD COLUMN clearance_level VARCHAR(50)"))
        
        # Add location column if not exists
        if 'location' not in existing_columns:
            print("Adding location column...")
            db.execute(text("ALTER TABLE users ADD COLUMN location VARCHAR(100)"))
        
        # Add created_at column if not exists
        if 'created_at' not in existing_columns:
            print("Adding created_at column...")
            db.execute(text("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW()"))
        
        # Add updated_at column if not exists
        if 'updated_at' not in existing_columns:
            print("Adding updated_at column...")
            db.execute(text("ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT NOW()"))
        
        # Update existing records with default values
        print("\n📝 Updating existing records...")
        db.execute(text("""
            UPDATE users 
            SET 
                is_active = COALESCE(is_active, TRUE),
                is_verified = COALESCE(is_verified, FALSE),
                created_at = COALESCE(created_at, NOW()),
                updated_at = COALESCE(updated_at, NOW())
        """))
        
        # Commit changes
        db.commit()
        
        # Verify updated structure
        print("\n✅ Verifying updated table structure...")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'users' 
            ORDER BY ordinal_position
        """))
        
        updated_columns = [row[0] for row in result.fetchall()]
        print(f"Updated columns: {updated_columns}")
        
        # Check data
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"✅ Users table updated successfully - {count} records")
        
        # Show sample data
        result = db.execute(text("SELECT id, email, name, is_active, is_verified, created_at FROM users LIMIT 5"))
        print("\n📊 Sample data:")
        for row in result.fetchall():
            print(f"  ID: {row[0]}, Email: {row[1]}, Name: {row[2]}, Active: {row[3]}, Verified: {row[4]}, Created: {row[5]}")
        
        db.close()
        print("\n🎉 Users table update completed successfully!")
        
    except Exception as e:
        print(f"❌ Error updating users table: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Starting users table update...")
    print("⚠️  This will modify the existing users table structure!")
    
    confirm = input("Are you sure you want to continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Table update cancelled.")
        sys.exit(0)
    
    success = update_users_table()
    if success:
        print("\n✨ Next steps:")
        print("1. Restart the backend server")
        print("2. Test the /users API endpoint")
        print("3. Check the frontend user list page")
    else:
        print("\n❌ Table update failed. Please check the error messages above.")
        sys.exit(1)
