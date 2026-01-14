"""
Updated insert_db.py - Uses unified database layer
No more mixing execution layers
"""

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
from markitdown import MarkItDown
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from database.unified_db import db

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")


def extract_text_from_file(file_path: str) -> str:
    """Extract text content from various file formats"""
    try:
        md = MarkItDown(enable_plugins=True)
        result = md.convert(file_path)
        return result.text_content
    except Exception as e:
        print(f"❌ Error extracting text from {file_path}: {e}")
        raise


def clean_sql_query(sql_query: str) -> str:
    """Clean SQL query by removing markdown formatting"""
    sql_query = re.sub(r'```sql\s*', '', sql_query, flags=re.IGNORECASE)
    sql_query = re.sub(r'```\s*', '', sql_query)
    sql_query = sql_query.strip()
    sql_query = re.sub(r'\n\s*\n', '\n', sql_query)
    sql_query = re.sub(r' +', ' ', sql_query)
    return sql_query


def get_schema_for_llm() -> str:
    """Get current database schema - only existing tables"""
    existing_tables = db.get_existing_tables()
    
    schema_info = "Available tables in database:\n"
    
    table_descriptions = {
        'departments': 'id (serial), name (varchar), description (text), office_location (varchar), contact_email (varchar), phone (varchar)',
        'programs': 'id (serial), department_id (int FK), name (varchar), degree_type (varchar), duration_years (int), description (text), career_outcomes (text)',
        'courses': 'id (serial), program_id (int FK), code (varchar), name (varchar), credits (int), semester (varchar), description (text)',
        'exams': 'id (serial), course_id (int FK), exam_type (varchar), exam_date (date), start_time (time), duration_minutes (int), total_marks (int), location (varchar), instructions (text)',
        'faculty_members': 'id (serial), department_id (int FK), name (varchar), title (varchar), email (varchar), office (varchar), office_hours (varchar), bio (text)',
        'admissions': 'id (serial), program_id (int FK), requirements (text), application_deadline (date), tuition_fee (numeric), scholarships (text)',
        'academic_calendar': 'id (serial), event_name (varchar), start_date (date), end_date (date), description (text)',
        'faqs': 'id (serial), category (varchar), question (varchar), answer (text), keywords (varchar), last_updated (timestamp)',
        'campus_services': 'id (serial), name (varchar), description (text), location (varchar), working_hours (varchar), contact_info (varchar)',
        'student_clubs': 'id (serial), name (varchar), category (varchar), description (text), contact_email (varchar)'
    }
    
    for table in existing_tables:
        desc = table_descriptions.get(table, 'Schema not documented')
        schema_info += f"\n- {table}: {desc}"
    
    return schema_info


def create_sql_generation_chain(llm: ChatMistralAI) -> Any:
    """Create LangChain chain for generating INSERT queries"""
    
    schema_info = get_schema_for_llm()
    existing_tables = db.get_existing_tables()
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", f"""You are a PostgreSQL expert. Generate INSERT queries from unstructured text.

{schema_info}

CRITICAL RULES:
1. ONLY generate INSERT for tables listed above
2. Return ONLY SQL statements, no markdown or explanations
3. Handle foreign keys with subqueries: (SELECT id FROM table WHERE condition LIMIT 1)
4. Order: departments → programs → courses → exams → faculty_members → admissions → others
5. Use single quotes for strings, double single quotes for escaping ('')
6. Dates format: 'YYYY-MM-DD', times: 'HH:MM:SS'
7. Multiple records: separate with semicolon
8. If you can't find data for a required field, use NULL
9. DO NOT add markdown code blocks

Available tables: {', '.join(existing_tables)}

Example:
Text: "Computer Science dept in Building A, email cs@uni.edu"
SQL: INSERT INTO departments (name, office_location, contact_email) VALUES ('Computer Science', 'Building A', 'cs@uni.edu');
"""),
        ("user", "Text: {text}\nFile: {filename}\n\nGenerate INSERT queries:")
    ])
    
    chain = (
        {
            "text": RunnablePassthrough(),
            "filename": RunnablePassthrough()
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )
    
    return chain


def add_duplicate_handling(statements: List[str]) -> List[str]:
    """Add ON CONFLICT or INSERT OR IGNORE to prevent duplicates"""
    result = []
    is_sqlite = 'sqlite' in db.database_url.lower()
    
    for stmt in statements:
        stmt_upper = stmt.upper()
        
        if not stmt_upper.startswith('INSERT'):
            result.append(stmt)
            continue
        
        # Check if duplicate handling already exists
        if 'ON CONFLICT' in stmt_upper or 'INSERT OR IGNORE' in stmt_upper:
            result.append(stmt)
            continue
        
        if is_sqlite:
            # SQLite: use INSERT OR IGNORE
            stmt = stmt.replace('INSERT INTO', 'INSERT OR IGNORE INTO', 1)
        else:
            # PostgreSQL: use ON CONFLICT DO NOTHING
            # Extract primary key column (usually 'id')
            match = re.search(r'INSERT INTO\s+(\w+)\s*\((.*?)\)', stmt, re.IGNORECASE)
            if match:
                # Add ON CONFLICT clause at the end
                if not stmt.rstrip().endswith(';'):
                    stmt = stmt.rstrip() + ' ON CONFLICT DO NOTHING;'
                else:
                    stmt = stmt.rstrip()[:-1] + ' ON CONFLICT DO NOTHING;'
        
        result.append(stmt)
    
    return result


def sort_statements_by_dependencies(statements: List[str]) -> List[str]:
    """Sort INSERT statements by table dependency"""
    table_order = {
        'departments': 1,
        'programs': 2,
        'courses': 3,
        'exams': 4,
        'faculty_members': 5,
        'admissions': 6,
        'academic_calendar': 7,
        'faqs': 7,
        'campus_services': 7,
        'student_clubs': 7,
    }
    
    def get_priority(stmt: str) -> int:
        match = re.search(r"INSERT\s+INTO\s+(\w+)", stmt, re.IGNORECASE)
        table = match.group(1).lower() if match else 'unknown'
        return table_order.get(table, 99)
    
    return sorted(statements, key=get_priority)


def process_file_and_insert(file_path: str, filename: Optional[str] = None) -> Dict[str, Any]:
    """
    Process file and insert into database
    Uses unified DB layer - single source of truth
    """
    if filename is None:
        filename = os.path.basename(file_path)
    
    print(f"\n📄 Processing file: {filename}")
    
    # Step 1: Extract text
    try:
        text = extract_text_from_file(file_path)
        print(f"✓ Extracted {len(text)} characters")
    except Exception as e:
        return {
            "success": False,
            "error": f"Text extraction failed: {str(e)}",
            "file": filename
        }
    
    if not text.strip():
        return {
            "success": False,
            "error": "No text content extracted",
            "file": filename
        }
    
    # Step 2: Initialize LLM
    try:
        llm = ChatMistralAI(
            mistral_api_key=MISTRAL_API_KEY,
            model=MISTRAL_MODEL,
            temperature=0.1
        )
        print("✓ LLM initialized")
    except Exception as e:
        return {
            "success": False,
            "error": f"LLM initialization failed: {str(e)}",
            "file": filename
        }
    
    # Step 3: Generate SQL
    try:
        chain = create_sql_generation_chain(llm)
        sql_query = chain.invoke({"text": text, "filename": filename})
        print(f"✓ SQL generated ({len(sql_query)} chars)")
    except Exception as e:
        return {
            "success": False,
            "error": f"SQL generation failed: {str(e)}",
            "file": filename
        }
    
    # Step 4: Clean and parse SQL
    sql_query = clean_sql_query(sql_query)
    
    sql_statements = []
    for stmt in sql_query.split(';'):
        stmt = stmt.strip()
        if stmt and stmt.upper().startswith('INSERT'):
            sql_statements.append(stmt)
    
    print(f"✓ Parsed {len(sql_statements)} INSERT statements")
    
    # Step 5: Filter for existing tables only
    existing_tables = db.get_existing_tables()
    filtered_statements = []
    
    for stmt in sql_statements:
        match = re.search(r"INSERT\s+INTO\s+(\w+)", stmt, re.IGNORECASE)
        if match:
            table = match.group(1)
            if table in existing_tables:
                filtered_statements.append(stmt)
                print(f"  ✓ Table '{table}' exists")
            else:
                print(f"  ⚠️  Skipping table '{table}' (doesn't exist)")
    
    sql_statements = sort_statements_by_dependencies(filtered_statements)
    print(f"✓ Filtered and sorted {len(sql_statements)} statements")
    
    # Step 5b: Add duplicate handling (ON CONFLICT / INSERT OR IGNORE)
    sql_statements = add_duplicate_handling(sql_statements)
    print(f"✓ Added duplicate prevention")
    
    # Step 6: Execute statements
    execution_results = []
    count_before = {}
    
    # Get counts before insertion
    for table in existing_tables:
        count_before[table] = db.count_rows(table)
    
    print("\n📊 Initial row counts:")
    for table, count in count_before.items():
        print(f"  {table}: {count}")
    
    # Execute each statement
    for i, stmt in enumerate(sql_statements, 1):
        result = db.execute_sql_statement(stmt)
        execution_results.append(result)
        
        if result["success"]:
            print(f"  ✓ Statement {i} executed")
        else:
            print(f"  ❌ Statement {i} failed: {result['error']}")
    
    # Step 7: Verify insertion
    print("\n✅ Verification (checking actual DB state):")
    all_successful = True
    verification = {}
    
    for table in existing_tables:
        count_after = db.count_rows(table)
        inserted = count_after - count_before[table]
        
        verification[table] = {
            "before": count_before[table],
            "after": count_after,
            "inserted": inserted
        }
        
        if inserted > 0:
            print(f"  ✓ {table}: {count_before[table]} → {count_after} (+{inserted})")
        else:
            print(f"  - {table}: {count_after} (no change)")
    
    # Determine overall success
    all_successful = any(v["inserted"] > 0 for v in verification.values())
    
    return {
        "success": all_successful,
        "file": filename,
        "statements_executed": len(sql_statements),
        "execution_results": execution_results,
        "verification": verification,
        "total_rows_inserted": sum(v["inserted"] for v in verification.values())
    }


def process_multiple_files(file_paths: List[str]) -> List[Dict[str, Any]]:
    """Process multiple files and return individual results"""
    results: List[Dict[str, Any]] = []
    for fp in file_paths:
        try:
            res = process_file_and_insert(fp)
        except Exception as e:
            res = {"success": False, "error": str(e), "file": os.path.basename(fp)}
        results.append(res)
    return results


def process_folder(folder_path: str, file_extensions: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Process all files in a folder (optionally filter by extensions)"""
    results: List[Dict[str, Any]] = []
    for root, _, files in os.walk(folder_path):
        for fname in files:
            if file_extensions:
                ext = fname.rsplit('.', 1)[-1].lower() if '.' in fname else ''
                if ext not in [e.lower().lstrip('.') for e in file_extensions]:
                    continue
            fp = os.path.join(root, fname)
            try:
                res = process_file_and_insert(fp)
            except Exception as e:
                res = {"success": False, "error": str(e), "file": os.path.basename(fp)}
            results.append(res)
    return results


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python insert_db.py <file_path>")
        sys.exit(1)
    
    result = process_file_and_insert(sys.argv[1])
    
    print("\n" + "="*60)
    if result["success"]:
        print(f"✅ SUCCESS: {result['total_rows_inserted']} rows inserted")
        for table, info in result["verification"].items():
            if info["inserted"] > 0:
                print(f"   {table}: +{info['inserted']}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
    print("="*60)

