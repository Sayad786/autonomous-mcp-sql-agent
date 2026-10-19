"""Model Context Protocol (MCP) Database Tool Server.
Implements the standard Anthropic MCP specification for warehouse schema discovery and execution.
"""

from typing import List, Dict, Any
from src.db_engine import DatabaseEngine
from src.guardrails import SQLGuardrails

class MCPSQLServer:
    """Model Context Protocol (MCP) server exposing standardized database tools."""

    def __init__(self, db_engine: DatabaseEngine = None):
        self.db = db_engine or DatabaseEngine()

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns standard Anthropic tool definitions conforming to the MCP specification."""
        return [
            {
                "name": "list_tables",
                "description": "Lists all available database tables in the enterprise warehouse.",
                "input_schema": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            },
            {
                "name": "describe_table",
                "description": "Retrieves the exact column names, data types, and 3 sample rows for a specified table.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "The exact name of the table to inspect (e.g., 'accounts', 'leads', 'campaigns', 'subscriptions')."
                        }
                    },
                    "required": ["table_name"]
                }
            },
            {
                "name": "execute_sql",
                "description": "Executes a validated, read-only SQL query against the enterprise warehouse. Automatically audited.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "A valid SELECT or CTE SQL statement to execute."
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "explain_sql",
                "description": "Returns the physical execution plan and cost estimates for a SQL statement before running it.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The SQL query to explain."
                        }
                    },
                    "required": ["query"]
                }
            }
        ]

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches an MCP tool call to the corresponding handler."""
        if tool_name == "list_tables":
            return self._list_tables()
        elif tool_name == "describe_table":
            table_name = arguments.get("table_name", "").strip()
            return self._describe_table(table_name)
        elif tool_name == "execute_sql":
            query = arguments.get("query", "").strip()
            return self._execute_sql(query)
        elif tool_name == "explain_sql":
            query = arguments.get("query", "").strip()
            return self._explain_sql(query)
        else:
            return {
                "error": f"Unknown MCP tool '{tool_name}'. Available: list_tables, describe_table, execute_sql, explain_sql"
            }

    def _list_tables(self) -> Dict[str, Any]:
        res = self.db.execute_query("SHOW TABLES;")
        if not res["success"]:
            return {"error": res["error"]}
        tables = [row[0] for row in res["rows"] if row[0] != "query_telemetry"]
        return {
            "tables": tables,
            "count": len(tables)
        }

    def _describe_table(self, table_name: str) -> Dict[str, Any]:
        if not table_name:
            return {"error": "table_name is required"}

        # Fetch Schema
        schema_res = self.db.execute_query(f"DESCRIBE {table_name};")
        if not schema_res["success"]:
            return {"error": f"Table '{table_name}' does not exist or cannot be described: {schema_res['error']}"}

        columns = [{"column_name": row[0], "data_type": row[1], "nullable": row[2]} for row in schema_res["rows"]]

        # Fetch 3 Sample Rows
        sample_res = self.db.execute_query(f"SELECT * FROM {table_name} LIMIT 3;")
        sample_rows = sample_res["rows"] if sample_res["success"] else []

        return {
            "table_name": table_name,
            "columns": columns,
            "sample_rows": sample_rows
        }

    def _execute_sql(self, query: str) -> Dict[str, Any]:
        # 1. Enforce Guardrails
        is_safe, sanitized_or_reason = SQLGuardrails.validate_safety(query)
        if not is_safe:
            return {
                "success": False,
                "error": f"Guardrail Violation: {sanitized_or_reason}",
                "query": query
            }

        # 2. Execute
        res = self.db.execute_query(sanitized_or_reason)
        return {
            **res,
            "executed_query": sanitized_or_reason
        }

    def _explain_sql(self, query: str) -> Dict[str, Any]:
        is_safe, sanitized_or_reason = SQLGuardrails.validate_safety(query)
        if not is_safe:
            return {"error": f"Guardrail Violation: {sanitized_or_reason}"}
        return self.db.explain_query(sanitized_or_reason)
