"""Deterministic Security & Safety Guardrails for Database Agents.
Validates queries against SQL injection, destructive DDL/DML, and multi-statement exploits.
"""

import re
from typing import Tuple, List
import sqlparse

class SQLGuardrails:
    """Security Guardrails enforcing read-only sandboxed database operations."""

    DISALLOWED_KEYWORDS = [
        "DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT", 
        "ALTER", "CREATE", "REPLACE", "GRANT", "REVOKE", 
        "EXECUTE", "MERGE", "CALL", "VACUUM", "COPY"
    ]

    @classmethod
    def validate_safety(cls, sql_query: str) -> Tuple[bool, str]:
        """Validates that a SQL query is strictly read-only and safe to execute.
        Returns: (is_safe: bool, reason_or_sanitized_sql: str)
        """
        if not sql_query or not sql_query.strip():
            return False, "Empty SQL query provided."

        clean_query = sql_query.strip().rstrip(";")

        # 1. Parse SQL statements using sqlparse
        parsed = sqlparse.parse(clean_query)
        if len(parsed) > 1:
            return False, "Security Violation: Multiple SQL statements detected in a single execution batch."

        if not parsed:
            return False, "Invalid SQL syntax: Unable to parse query."

        statement = parsed[0]
        statement_type = statement.get_type()

        # 2. Allow only SELECT or WITH (Common Table Expressions)
        if statement_type not in ("SELECT", "UNKNOWN"):
            return False, f"Security Violation: Disallowed statement type '{statement_type}'. Only SELECT or CTEs are permitted."

        # 3. Check for disallowed destructive keywords via token examination
        upper_query = clean_query.upper()
        for kw in cls.DISALLOWED_KEYWORDS:
            # Word boundary regex check to avoid matching column substrings like 'created_at' for 'CREATE'
            pattern = rf"\b{kw}\b"
            if re.search(pattern, upper_query):
                # Verify if it's not a legitimate select alias or column name
                return False, f"Security Violation: Query contains prohibited keyword '{kw}'."

        # 4. Check for system prompt override / injection signatures
        injection_patterns = [
            r"system\s+prompt\s+override",
            r"ignore\s+(all\s+)?previous\s+instructions",
            r"--.*drop",
            r"/\*.*drop.*\*/"
        ]
        for pat in injection_patterns:
            if re.search(pat, upper_query, re.IGNORECASE):
                return False, f"Security Violation: Potential prompt injection or comment evasion detected."

        return True, clean_query
