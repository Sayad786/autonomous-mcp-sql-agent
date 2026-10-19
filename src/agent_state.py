"""Agent State Definition for LangGraph Cyclical Workflow."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class AgentState(BaseModel):
    """Shared state container across all LangGraph nodes."""
    user_query: str = Field(description="The original natural language question from the user")
    available_tables: List[str] = Field(default_factory=list, description="Tables listed in the warehouse")
    relevant_schemas: Dict[str, Any] = Field(default_factory=dict, description="Detailed schemas for inspected tables")
    generated_sql: Optional[str] = Field(default=None, description="The candidate SQL query produced by the model")
    sql_explanation: Optional[str] = Field(default=None, description="Natural language explanation of the generated SQL")
    execution_result: Optional[Dict[str, Any]] = Field(default=None, description="Output from the MCP execution tool")
    error_message: Optional[str] = Field(default=None, description="SQL runtime or guardrail error message if any")
    reflection_count: int = Field(default=0, description="Number of self-correction reflection loops executed")
    reflection_notes: List[str] = Field(default_factory=list, description="Notes recorded during reflection for query tuning")
    final_answer: Optional[str] = Field(default=None, description="The final synthesized executive answer")
    execution_trace: List[Dict[str, Any]] = Field(default_factory=list, description="Step-by-step trace of node transitions")
