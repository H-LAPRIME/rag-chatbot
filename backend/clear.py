"""
Script to clear data from database with multiple options:
1. Clear all tables
2. Clear specific table
3. Delete specific rows by IDs
"""

import os
import sys
from dotenv import load_dotenv
load_dotenv()
from sqlalchemy import text
from database.unified_db import db

def clear_all_tables() -> dict:
    """Delete all data from all tables in the database"""
    existing_tables = db.get_existing_tables()
    
    if not existing_tables:
        print("❌ No tables found in database")
        return {"success": False, "error": "No tables found"}
    
    print("🗑️  Clearing all tables...\n")
    
    # Get row counts before clearing
    counts_before = {}
    for table in existing_tables:
        counts_before[table] = db.count_rows(table)
    
    print("📊 Row counts BEFORE clearing:")
    for table, count in counts_before.items():
        print(f"  {table}: {count}")
    
    # Clear each table
    cleared = []
    errors = []
    
    is_sqlite = 'sqlite' in db.database_url.lower()
    
    for table in existing_tables:
        try:
            if is_sqlite:
                # SQLite: use DELETE FROM
                stmt = f"DELETE FROM {table}"
            else:
                # PostgreSQL: use TRUNCATE (faster) with CASCADE
                stmt = f"TRUNCATE TABLE {table} CASCADE"
            
            result = db.execute_sql_statement(stmt)
            
            if result["success"]:
                cleared.append(table)
                print(f"  ✓ {table} cleared")
            else:
                errors.append({"table": table, "error": result.get("error")})
                print(f"  ❌ {table} failed: {result.get('error')}")
        except Exception as e:
            errors.append({"table": table, "error": str(e)})
            print(f"  ❌ {table} failed: {str(e)}")
    
    # Verify clearing
    print("\n✅ Row counts AFTER clearing:")
    counts_after = {}
    for table in existing_tables:
        counts_after[table] = db.count_rows(table)
        print(f"  {table}: {counts_after[table]}")
    
    all_cleared = all(count == 0 for count in counts_after.values())
    
    return {
        "success": all_cleared and len(errors) == 0,
        "tables_cleared": cleared,
        "errors": errors,
        "counts_before": counts_before,
        "counts_after": counts_after,
        "total_rows_deleted": sum(counts_before.values())
    }


def clear_specific_table(table_name: str) -> dict:
    """Delete all data from a specific table"""
    existing_tables = db.get_existing_tables()
    
    if table_name not in existing_tables:
        return {"success": False, "error": f"Table '{table_name}' not found"}
    
    count_before = db.count_rows(table_name)
    print(f"\n📊 Table '{table_name}' has {count_before} rows")
    
    is_sqlite = 'sqlite' in db.database_url.lower()
    
    try:
        if is_sqlite:
            stmt = f"DELETE FROM {table_name}"
        else:
            stmt = f"TRUNCATE TABLE {table_name} CASCADE"
        
        result = db.execute_sql_statement(stmt)
        
        if result["success"]:
            count_after = db.count_rows(table_name)
            print(f"✓ Table '{table_name}' cleared: {count_before} → {count_after}")
            return {
                "success": True,
                "table": table_name,
                "rows_deleted": count_before,
                "rows_before": count_before,
                "rows_after": count_after
            }
        else:
            return {"success": False, "error": result.get("error")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def delete_rows_by_ids(table_name: str, ids: list) -> dict:
    """Delete specific rows by ID from a table"""
    existing_tables = db.get_existing_tables()
    
    if table_name not in existing_tables:
        return {"success": False, "error": f"Table '{table_name}' not found"}
    
    if not ids:
        return {"success": False, "error": "No IDs provided"}
    
    count_before = db.count_rows(table_name)
    
    # Convert IDs to comma-separated string (with quotes for safety)
    id_list = ','.join(str(id).strip() for id in ids)
    
    try:
        stmt = f"DELETE FROM {table_name} WHERE id IN ({id_list})"
        result = db.execute_sql_statement(stmt)
        
        if result["success"]:
            count_after = db.count_rows(table_name)
            rows_deleted = count_before - count_after
            print(f"✓ Deleted {rows_deleted} rows from '{table_name}': {count_before} → {count_after}")
            return {
                "success": True,
                "table": table_name,
                "ids_deleted": ids,
                "rows_deleted": rows_deleted,
                "rows_before": count_before,
                "rows_after": count_after
            }
        else:
            return {"success": False, "error": result.get("error")}
    except Exception as e:
        return {"success": False, "error": str(e)}


def show_menu():
    """Display interactive menu"""
    print("\n" + "="*60)
    print("DATABASE CLEANUP UTILITY")
    print("="*60)
    # show which database is in use
    try:
        print(f"\nConnected DB: {db.database_url}")
    except Exception:
        pass
    
    print("\nChoose an option:")
    print("  1️⃣  Clear ALL tables (delete all data)")
    print("  2️⃣  Clear SPECIFIC table")
    print("  3️⃣  Delete specific rows by IDs")
    print("  0️⃣  Exit")
    
    # flush output to ensure prompt appears immediately in terminals
    sys.stdout.flush()
    choice = input("\nEnter your choice (0-3): ").strip()
    return choice


def main():
    """Main menu loop"""
    while True:
        choice = show_menu()
        
        if choice == '0':
            print("👋 Bye!")
            break
        
        elif choice == '1':
            confirm = input("\n⚠️  WARNING: This will DELETE ALL data from all tables!\nType 'yes' to confirm: ")
            
            if confirm.lower() != 'yes':
                print("❌ Cancelled.")
                continue
            
            result = clear_all_tables()
            
            print("\n" + "="*60)
            if result["success"]:
                print(f"✅ SUCCESS: All {len(result['tables_cleared'])} tables cleared")
                print(f"   Total rows deleted: {result['total_rows_deleted']}")
            else:
                print("❌ FAILED: Some errors occurred")
                errors = result.get("errors") or []
                if errors:
                    print("   Errors:")
                    for err in errors:
                        # err may be a dict with table/error or other shape
                        if isinstance(err, dict) and "table" in err and "error" in err:
                            print(f"     - {err['table']}: {err['error']}")
                        else:
                            print(f"     - {err}")
            print("="*60)
        
        elif choice == '2':
            # List available tables
            tables = db.get_existing_tables()
            
            if not tables:
                print("❌ No tables found")
                continue
            
            print("\n📋 Available tables:")
            for i, table in enumerate(tables, 1):
                count = db.count_rows(table)
                print(f"  {i}. {table} ({count} rows)")
            
            table_choice = input("\nEnter table name to clear: ").strip()
            
            if table_choice not in tables:
                print(f"❌ Table '{table_choice}' not found")
                continue
            
            confirm = input(f"\n⚠️  WARNING: This will DELETE ALL data from '{table_choice}'!\nType 'yes' to confirm: ")
            
            if confirm.lower() != 'yes':
                print("❌ Cancelled.")
                continue
            
            result = clear_specific_table(table_choice)
            
            print("\n" + "="*60)
            if result["success"]:
                print(f"✅ SUCCESS: Table '{table_choice}' cleared")
                print(f"   Rows deleted: {result['rows_deleted']}")
            else:
                print(f"❌ FAILED: {result.get('error')}")
            print("="*60)
        
        elif choice == '3':
            # List available tables
            tables = db.get_existing_tables()
            
            if not tables:
                print("❌ No tables found")
                continue
            
            print("\n📋 Available tables:")
            for i, table in enumerate(tables, 1):
                count = db.count_rows(table)
                print(f"  {i}. {table} ({count} rows)")
            
            table_choice = input("\nEnter table name: ").strip()
            
            if table_choice not in tables:
                print(f"❌ Table '{table_choice}' not found")
                continue
            
            # Get sample IDs
            print(f"\n📊 Sample IDs from '{table_choice}':")
            try:
                with db.engine().connect() as conn:
                    res = conn.execute(text(f"SELECT id FROM {table_choice} LIMIT 10"))
                    sample_ids = [row[0] for row in res.fetchall()]
                    if sample_ids:
                        print(f"  Example IDs: {', '.join(str(id) for id in sample_ids)}")
                    else:
                        print(f"  No rows in table")
                        continue
            except Exception as e:
                print(f"  Error fetching IDs: {e}")
                continue
            
            ids_input = input("\nEnter IDs to delete (comma-separated, e.g. 1,2,5): ").strip()
            
            if not ids_input:
                print("❌ No IDs provided")
                continue
            
            try:
                ids = [int(id.strip()) for id in ids_input.split(',')]
            except ValueError:
                print("❌ Invalid ID format. Use numbers separated by commas")
                continue
            
            confirm = input(f"\n⚠️  WARNING: This will DELETE {len(ids)} rows from '{table_choice}'!\nType 'yes' to confirm: ")
            
            if confirm.lower() != 'yes':
                print("❌ Cancelled.")
                continue
            
            result = delete_rows_by_ids(table_choice, ids)
            
            print("\n" + "="*60)
            if result["success"]:
                print(f"✅ SUCCESS: Rows deleted from '{table_choice}'")
                print(f"   IDs deleted: {result['ids_deleted']}")
                print(f"   Rows deleted: {result['rows_deleted']}")
            else:
                print(f"❌ FAILED: {result.get('error')}")
            print("="*60)
        
        else:
            print("❌ Invalid choice. Please enter 0-3")


if __name__ == "__main__":
    main()
