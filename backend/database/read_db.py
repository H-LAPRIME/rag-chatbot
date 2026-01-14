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
    return """
 academic_calendar(
  id INTEGER PRIMARY KEY,
  event_name VARCHAR,
  start_date DATE,
  end_date DATE,
  description TEXT
)

admissions(
  id INTEGER PRIMARY KEY,
  program_id INTEGER REFERENCES programs(id),
  requirements TEXT,
  application_deadline DATE,
  tuition_fee NUMERIC,
  scholarships TEXT
)

campus_services(
  id INTEGER PRIMARY KEY,
  name VARCHAR,
  description TEXT,
  location VARCHAR,
  working_hours VARCHAR,
  contact_info VARCHAR
)

courses(
  id INTEGER PRIMARY KEY,
  program_id INTEGER REFERENCES programs(id),
  code VARCHAR,
  name VARCHAR,
  credits INTEGER,
  description TEXT,
  semester VARCHAR
)

departments(
  id INTEGER PRIMARY KEY,
  name VARCHAR,
  description TEXT,
  office_location VARCHAR,
  contact_email VARCHAR,
  phone VARCHAR
)

faculty_members(
  id INTEGER PRIMARY KEY,
  department_id INTEGER REFERENCES departments(id),
  name VARCHAR,
  title VARCHAR,
  email VARCHAR,
  office VARCHAR,
  office_hours VARCHAR,
  image VARCHAR,
  bio TEXT
)

faqs(
  id INTEGER PRIMARY KEY,
  category VARCHAR,
  question TEXT,
  answer TEXT,
  keywords TEXT,
  last_updated TIMESTAMP
)

programs(
  id INTEGER PRIMARY KEY,
  department_id INTEGER REFERENCES departments(id),
  name VARCHAR,
  degree_type VARCHAR,
  duration_years INTEGER,
  description TEXT,
  career_outcomes TEXT
)

student_clubs(
  id INTEGER PRIMARY KEY,
  name VARCHAR,
  category VARCHAR,
  description TEXT,
  contact_email VARCHAR
)

DATABASE RELATIONSHIPS:

programs.department_id → departments.id
courses.program_id → programs.id
admissions.program_id → programs.id
faculty_members.department_id → departments.id

 """


def create_sql_generation_chain(llm: ChatMistralAI):
    schema_info = get_schema_for_llm()
    existing_tables = db.get_existing_tables()


    prompt_template = ChatPromptTemplate.from_messages([
        (
            "system",
            """
You are a PostgreSQL expert and a search-oriented SQL assistant.

Your task is to generate safe, read-only SELECT queries that retrieve the
MOST RELEVANT results based on the user's question, even if:
- the user misspells words
- the user uses partial or approximate names
- the user guesses an incorrect value

Prefer best-effort retrieval over exact matching.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATABASE SCHEMA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{schema_info}

Available tables: {existing_tables}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Generate ONLY SELECT statements.
2. Use ONLY tables listed above.
3. Return ONLY raw SQL (no markdown, no explanations).
4. Use single quotes for strings and proper escaping.
5. Do NOT modify data (no INSERT, UPDATE, DELETE).
6. Do NOT return primary keys or foreign keys.
7. Use LIMIT when results may be large.
8. Prefer simple and readable SQL.
9. If context references joins, use explicit JOIN ... ON clauses.

CRITICAL RULES FOR USER-FACING QUERIES:

- Never return primary keys or foreign keys (IDs) to the user.
- If a query requires filtering by an ID (e.g., course_id, department_id), resolve it internally with a JOIN to fetch the human-readable field (name, title, code).
- Always return only meaningful, user-facing fields.
- Example: Instead of returning course_id = 12, return course_name = 'Computer Science'.
- All joins should be explicit and readable.
- The user should never see technical database references.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEARCH & MATCHING RULES (VERY IMPORTANT)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- NEVER rely on exact string matching unless explicitly required.
- Prefer case-insensitive and partial matching using:
  - ILIKE
  - LOWER(column)
  - wildcard patterns (%)

- If a filter value may be misspelled or uncertain:
  - Use ILIKE '%value%' instead of '='

- If the user references an entity (department, course, exam, instructor):
  - Search across relevant text columns (name, title, code, description).

- If no confident filter can be inferred:
  - Return a reasonable sample of relevant rows instead of an empty result.

- RESPECT SCHEMA FIELDS AND METADATA DO NOT HALLUCINATE FIELDS OR TABLES (very important)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUERY STRATEGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Identify the main entity mentioned in the question.
2. Identify suitable text columns for flexible searching.
3. Apply partial, case-insensitive filters when needed.
4. Always include a LIMIT (typically 5–10).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EXAMPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User: "informatique department"
SQL:
SELECT name, description
FROM departments
WHERE name ILIKE '%info%' OR description ILIKE '%info%'
LIMIT 5;

User: "math departmant"
SQL:
SELECT name, description
FROM departments
WHERE name ILIKE '%math%'
LIMIT 5;

User: "random department name"
SQL:
SELECT name, description
FROM departments
LIMIT 5;

User: "Show latest 5 exams for course CS101"
SQL:
SELECT course_name, exam_date
FROM exams
WHERE course_name ILIKE '%CS101%'
ORDER BY exam_date DESC
LIMIT 5;
"""
        ),
        (
            "user",
            "Question: {question}\nContext: {context}\n\nGenerate the most relevant SELECT query:"
        )
    ])

    chain = (
        {
            "question": RunnablePassthrough(),
            "context": RunnablePassthrough(),
            "schema_info": lambda _: schema_info,
            "existing_tables": lambda _: ", ".join(existing_tables),
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
