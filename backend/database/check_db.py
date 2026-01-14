"""
Script to check database connection and list all tables with data
"""

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from database.unified_db import db

def check_connection() -> dict:
    """Check database connection and list tables"""
    
    print("🔗 Connecting to database...\n")
    
    try:
        # Test connection
        with db.engine().connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.scalar()
        print(f"✅ Connected to: {db.database_url}\n")
    except Exception as e:
        return {"success": False, "error": f"Connection failed: {str(e)}"}
    
    # Get all tables
    tables = db.get_existing_tables()
    
    if not tables:
        return {"success": False, "error": "No tables found"}
    
    print(f"📊 Found {len(tables)} tables:\n")
    
    table_info = {}
    
    # List each table with row count and sample data
    for table in tables:
        count = db.count_rows(table)
        table_info[table] = {"count": count, "data": []}
        
        print(f"  📋 {table}: {count} rows")
        
        # Get sample data (first 3 rows)
        try:
            with db.engine().connect() as conn:
                res = conn.execute(text(f"SELECT * FROM {table} LIMIT 3"))
                columns = res.keys()
                rows = [dict(r) for r in res.mappings().all()]
                
                if rows:
                    print(f"      Columns: {', '.join(columns)}")
                    for i, row in enumerate(rows, 1):
                        table_info[table]["data"].append(row)
                        print(f"      Row {i}: {row}")
                print()
        except Exception as e:
            print(f"      Error reading data: {e}\n")
    
    return {"success": True, "tables": table_info, "database": db.database_url}


if __name__ == "__main__":
    print("="*70)
    print("DATABASE CONNECTION CHECK")
    print("="*70 + "\n")
    
    result = check_connection()
    
    print("="*70)
    if result["success"]:
        print(f"✅ SUCCESS: Database is accessible")
        print(f"   Database: {result['database']}")
        print(f"   Tables: {len(result['tables'])}")
    else:
        print(f"❌ FAILED: {result['error']}")
    print("="*70)
