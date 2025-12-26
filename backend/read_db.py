import os
import re
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from sqlalchemy import text

# Load environment variables before importing UnifiedDB so DATABASE_URL / DB_* are available
load_dotenv()

from database.unified_db import db

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is required")


def clean_sql_query(sql_query: str) -> str:
    sql_query = re.sub(r'```sql\s*', '', sql_query, flags=re.IGNORECASE)
    sql_query = re.sub(r'```\s*', '', sql_query)
    sql_query = sql_query.strip()
    sql_query = re.sub(r'\n\s*\n', '\n', sql_query)
    sql_query = re.sub(r' +', ' ', sql_query)
    return sql_query


def get_schema_for_llm() -> str:
    existing_tables = db.get_existing_tables()
    schema_info = "Available tables in database:\n"

    # Minimal descriptions (kept similar to insert_db examples)
    for table in existing_tables:
        schema_info += f"\n- {table}: Schema not documented (use table columns as available)"

    return schema_info


def create_sql_generation_chain(llm: ChatMistralAI) -> Any:
    schema_info = get_schema_for_llm()
    existing_tables = db.get_existing_tables()

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", f"""You are a PostgreSQL expert. Generate safe SELECT queries from a user's question and optional context.

{schema_info}

CRITICAL RULES:
1. ONLY generate SELECT statements for tables listed above.
2. Return ONLY SQL statements, no markdown or explanations.
3. Use single quotes for strings and proper escaping.
4. If filtering by values, use WHERE clauses with sensible limits.
5. Use LIMIT when appropriate to avoid huge results.
6. If context references joins, prefer simple joins with explicit ON.
7. Do not modify data (no INSERT/UPDATE/DELETE).

Available tables: {', '.join(existing_tables)}

Example:
User: "Show latest 5 exams for course CS101"
SQL: SELECT * FROM exams WHERE course_id = (SELECT id FROM courses WHERE code = 'CS101' LIMIT 1) ORDER BY exam_date DESC LIMIT 5;
"""),
        ("user", "Question: {question}\nContext: {context}\n\nGenerate SELECT queries:")
    ])

    chain = (
        {
            "question": RunnablePassthrough(),
            "context": RunnablePassthrough()
        }
        | prompt_template
        | llm
        | StrOutputParser()
    )

    return chain


def process_query_and_select(question: str, context: Optional[str] = None) -> Dict[str, Any]:
    if context is None:
        context = ""

    try:
        llm = ChatMistralAI(
            mistral_api_key=MISTRAL_API_KEY,
            model=MISTRAL_MODEL,
            temperature=0.1
        )
    except Exception as e:
        return {"success": False, "error": f"LLM init failed: {e}"}

    try:
        chain = create_sql_generation_chain(llm)
        sql_text = chain.invoke({"question": question, "context": context})
    except Exception as e:
        return {"success": False, "error": f"SQL generation failed: {e}"}

    sql_text = clean_sql_query(sql_text)

    statements: List[str] = []
    for stmt in sql_text.split(';'):
        s = stmt.strip()
        if s and s.upper().startswith('SELECT'):
            statements.append(s)

    results = []
    errors = []

    # Execute SELECT statements and collect results
    for i, stmt in enumerate(statements, 1):
        try:
            with db.engine().connect() as conn:
                res = conn.execute(text(stmt))
                try:
                    rows = [dict(r) for r in res.mappings().all()]
                except Exception:
                    # fallback: try fetchall with tuples
                    rows = [list(r) for r in res.all()]
            results.append({"statement": stmt, "rows": rows, "rowcount": len(rows)})
        except Exception as e:
            errors.append({"statement": stmt, "error": str(e)})

    success = len(results) > 0 and len(errors) == 0

    return {
        "success": success,
        "generated_sql": sql_text,
        "results": results,
        "errors": errors
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python read_db.py '<question>' [optional context file path]")
        sys.exit(1)

    question = sys.argv[1]
    context = None
    if len(sys.argv) >= 3:
        ctx_path = sys.argv[2]
        try:
            with open(ctx_path, 'r', encoding='utf-8') as f:
                context = f.read()
        except Exception as e:
            print(f"Could not read context file: {e}")

    out = process_query_and_select(question, context)

    print('\n' + '='*60)
    if out.get('success'):
        print('✅ SUCCESS: Results retrieved')
        for r in out['results']:
            print('\nStatement:', r['statement'])
            print('Rows:', len(r['rows']))
            for row in r['rows'][:5]:
                print(' ', row)
    else:
        print('❌ FAILED:', out.get('error') or out.get('errors'))
    print('='*60)
