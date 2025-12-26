import os
from typing import List, Dict, Any, Optional
from urllib.parse import quote_plus
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import make_url

class UnifiedDB:
    """Small, simple DB helper: lazy engine, DB_* env support, sqlite fallback."""

    def __init__(self, database_url: Optional[str] = None):
        database_url = database_url or os.getenv("DATABASE_URL")
        if not database_url:
            host = os.getenv("DB_HOST")
            if host:
                user = quote_plus(os.getenv("DB_USER", ""))
                pwd = quote_plus(os.getenv("DB_PASS", ""))
                port = os.getenv("DB_PORT", "5432")
                name = os.getenv("DB_NAME", "postgres")
                ssl = os.getenv("DB_SSLMODE", "require")
                database_url = f"postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{name}?sslmode={ssl}"

        if not database_url:
            base = os.path.dirname(os.path.dirname(__file__))
            database_url = f"sqlite:///{os.path.join(base, 'data.db')}"

        # normalize postgres shorthand
        try:
            url = make_url(database_url)
            if url.drivername in ("postgres", "postgresql") and "+" not in url.drivername:
                database_url = database_url.replace(url.drivername, "postgresql+psycopg2", 1)
        except Exception:
            pass

        self.database_url = database_url
        self._engine = None

    def _engine_create(self):
        eng = create_engine(self.database_url, future=True)
        try:
            with eng.connect():
                pass
        except Exception:
            # fallback to sqlite
            base = os.path.dirname(os.path.dirname(__file__))
            fallback = f"sqlite:///{os.path.join(base,'data.db')}"
            eng.dispose()
            eng = create_engine(fallback, future=True)
            self.database_url = fallback
        return eng

    def engine(self):
        if self._engine is None:
            self._engine = self._engine_create()
        return self._engine

    def get_existing_tables(self) -> List[str]:
        try:
            return inspect(self.engine()).get_table_names()
        except Exception:
            return []

    def count_rows(self, table: str) -> int:
        try:
            with self.engine().connect() as c:
                r = c.execute(text(f"SELECT COUNT(*) FROM {table}"))
                return int(r.scalar_one_or_none() or 0)
        except Exception:
            return 0

    def execute_sql_statement(self, stmt: str) -> Dict[str, Any]:
        try:
            with self.engine().begin() as c:
                res = c.execute(text(stmt))
                return {"success": True, "rowcount": getattr(res, "rowcount", None)}
        except Exception as e:
            return {"success": False, "error": str(e)}


db = UnifiedDB()
