"""Database Engine Interface for Autonomous SQL Agent.
Provides safe, read-only connectivity and execution metrics against DuckDB (with Snowflake compatibility).
"""

import time
from typing import Dict, Any, List, Optional
import duckdb
from pathlib import Path

from src.config import Config

class DatabaseEngine:
    """Enterprise Database Engine providing safe read-only query execution."""

    def __init__(self, db_path: Path = Config.DB_PATH):
        self.db_path = db_path
        if not self.db_path.exists():
            from data.seed_enterprise_db import seed_database
            seed_database(self.db_path)

    def get_connection(self, read_only: bool = True) -> duckdb.DuckDBPyConnection:
        """Returns a DuckDB connection with read_only protection."""
        return duckdb.connect(str(self.db_path), read_only=read_only)

    def execute_query(self, sql_query: str, limit: int = Config.MAX_ROW_LIMIT) -> Dict[str, Any]:
        """Executes a SQL query safely and measures latency."""
        start_time = time.perf_counter()
        
        # Enforce limit if not already present on SELECT / CTE queries
        clean_sql = sql_query.strip().rstrip(";")
        upper_start = clean_sql.upper()
        if (upper_start.startswith("SELECT") or upper_start.startswith("WITH")) and "LIMIT" not in upper_start:
            clean_sql += f" LIMIT {limit}"

        try:
            conn = self.get_connection(read_only=True)
            rel = conn.execute(clean_sql)
            columns = [desc[0] for desc in rel.description] if rel.description else []
            rows = rel.fetchall()
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            conn.close()

            return {
                "success": True,
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "execution_time_ms": execution_time_ms,
                "error": None
            }
        except Exception as e:
            execution_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "execution_time_ms": execution_time_ms,
                "error": str(e)
            }

    def explain_query(self, sql_query: str) -> Dict[str, Any]:
        """Returns the physical execution plan and cost estimates."""
        explain_sql = f"EXPLAIN {sql_query.strip().rstrip(';')};"
        return self.execute_query(explain_sql)
