"""Unit & Integration Tests for Autonomous MCP SQL Agent."""

import pytest
from src.guardrails import SQLGuardrails
from src.mcp_server import MCPSQLServer
from src.agent_graph import AutonomousSQLAgent

def test_guardrails_allow_valid_select():
    valid_query = "SELECT account_name, annual_contract_value_usd FROM accounts WHERE tier = 'Enterprise';"
    is_safe, res = SQLGuardrails.validate_safety(valid_query)
    assert is_safe is True
    assert "accounts" in res

def test_guardrails_block_drop_table():
    bad_query = "DROP TABLE accounts;"
    is_safe, reason = SQLGuardrails.validate_safety(bad_query)
    assert is_safe is False
    assert "Security Violation" in reason

def test_guardrails_block_delete_from():
    bad_query = "DELETE FROM leads WHERE lead_score < 50;"
    is_safe, reason = SQLGuardrails.validate_safety(bad_query)
    assert is_safe is False
    assert "Security Violation" in reason

def test_guardrails_block_multi_statement_injection():
    bad_query = "SELECT * FROM accounts; DROP TABLE leads;"
    is_safe, reason = SQLGuardrails.validate_safety(bad_query)
    assert is_safe is False
    assert "Multiple SQL statements" in reason

def test_mcp_list_tables():
    mcp = MCPSQLServer()
    res = mcp.call_tool("list_tables", {})
    assert "tables" in res
    assert "accounts" in res["tables"]
    assert "leads" in res["tables"]
    assert "campaigns" in res["tables"]

def test_mcp_describe_table():
    mcp = MCPSQLServer()
    res = mcp.call_tool("describe_table", {"table_name": "accounts"})
    assert res["table_name"] == "accounts"
    cols = [c["column_name"] for c in res["columns"]]
    assert "account_id" in cols
    assert "annual_contract_value_usd" in cols

def test_agent_end_to_end_execution():
    agent = AutonomousSQLAgent()
    state = agent.run("Show top 5 enterprise accounts by ACV")
    assert state.execution_result is not None
    assert state.execution_result.get("success") is True
    assert state.execution_result.get("row_count") > 0
    assert "Executive Data Summary" in state.final_answer

def test_agent_self_correction_reflection():
    agent = AutonomousSQLAgent()
    # "test error" query triggers intentional initial syntax error in deterministic engine
    state = agent.run("Run a test error query to evaluate self-correction")
    assert state.reflection_count >= 1
    assert len(state.reflection_notes) >= 1
