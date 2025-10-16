"""
Test Database Connection
Run this to verify SQL Server connection is working
"""

from app.core.database import engine
from sqlalchemy import text

def test_connection():
    """Test basic database connectivity"""
    print("\n" + "="*60)
    print("TESTING DATABASE CONNECTION")
    print("="*60 + "\n")
    
    try:
        with engine.connect() as connection:
            # Test basic connection
            result = connection.execute(text("SELECT @@VERSION"))
            version = result.fetchone()[0]
            print("✅ Database connected successfully!")
            print(f"\nSQL Server version:")
            print(f"   {version[:80]}...")
            
            # Check database name
            result = connection.execute(text("SELECT DB_NAME()"))
            db_name = result.fetchone()[0]
            print(f"\n✅ Current database: {db_name}")
            
            # List all tables
            result = connection.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_TYPE = 'BASE TABLE'
                ORDER BY TABLE_NAME
            """))
            tables = [row[0] for row in result]
            
            if tables:
                print(f"\n✅ Found {len(tables)} tables:")
                for table in tables:
                    # Get row count for each table
                    try:
                        count_result = connection.execute(text(f"SELECT COUNT(*) FROM [{table}]"))
                        count = count_result.fetchone()[0]
                        print(f"   - {table:30s} ({count:,} rows)")
                    except:
                        print(f"   - {table:30s} (error counting)")
            else:
                print("\n⚠️  No tables found. Please run create_all.sql first!")
            
            # List all views
            result = connection.execute(text("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.VIEWS
                ORDER BY TABLE_NAME
            """))
            views = [row[0] for row in result]
            
            if views:
                print(f"\n✅ Found {len(views)} views:")
                for view in views:
                    print(f"   - {view}")
            
            print("\n" + "="*60)
            print("DATABASE TEST SUCCESSFUL! 🎉")
            print("="*60 + "\n")
            
    except Exception as e:
        print("\n" + "="*60)
        print("❌ DATABASE CONNECTION FAILED!")
        print("="*60)
        print(f"\nError: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check if SQL Server is running")
        print("   2. Verify credentials in .env file")
        print("   3. Ensure database 'SmartTrafficDB' exists")
        print("   4. Check if ODBC Driver 17 is installed")
        print("   5. Run: Get-Service | Where-Object {$_.Name -like '*SQL*'}")
        print("\n")


if __name__ == "__main__":
    test_connection()
