"""Streamlit Dashboard for Autonomous Database Reasoning Agent via Model Context Protocol (MCP) & LangGraph.
"""

import streamlit as st
import pandas as pd
import time

from src.agent_graph import AutonomousSQLAgent
from src.mcp_server import MCPSQLServer
from src.config import Config

# Page Configuration
st.set_page_config(
    page_title="Autonomous MCP Database Agent",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern enterprise aesthetics
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.5rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        font-size: 0.8rem;
        font-weight: 600;
        border-radius: 9999px;
        margin-right: 0.4rem;
        background-color: #e0e7ff;
        color: #3730a3;
    }
    .card-box {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .step-badge {
        font-weight: 700;
        color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "agent" not in st.session_state:
    st.session_state.agent = AutonomousSQLAgent()
if "mcp" not in st.session_state:
    st.session_state.mcp = MCPSQLServer()
if "last_state" not in st.session_state:
    st.session_state.last_state = None

# Sidebar: Warehouse Metadata & MCP Tool Inspector
with st.sidebar:
    st.image("https://raw.githubusercontent.com/modelcontextprotocol/specification/main/docs/assets/mcp-logo.png", width=120)
    st.markdown("### 🏛️ Model Context Protocol (MCP)")
    st.markdown("Standardized tool-calling server connecting **Claude 3.5 Sonnet** to enterprise database layers.")
    
    st.markdown("---")
    st.markdown("#### 📦 Warehouse Tables")
    tables_info = st.session_state.mcp.call_tool("list_tables", {})
    tables = tables_info.get("tables", [])
    
    selected_table = st.selectbox("Inspect Table Schema (via MCP):", tables)
    if selected_table:
        schema = st.session_state.mcp.call_tool("describe_table", {"table_name": selected_table})
        if "columns" in schema:
            st.caption(f"**Schema for `{selected_table}`:**")
            col_df = pd.DataFrame(schema["columns"])[["column_name", "data_type"]]
            st.dataframe(col_df, use_container_width=True, hide_index=True)
            
    st.markdown("---")
    st.markdown("#### 🛡️ Active Guardrails")
    st.markdown("""
    - **Read-Only Sandbox:** DDL/DML Blocked
    - **Injection Defense:** Regex + AST Filter
    - **Max Execution Rows:** 100 rows
    - **Query Timeout:** 10 seconds
    """)
    st.caption("Built by **Sayad Khalid Uddin**")

# Main Header
st.markdown('<div class="main-header">⚡ Autonomous Database Reasoning Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Anthropic Model Context Protocol (MCP) • LangGraph Cyclical State Machine • Self-Correction Reflection Loop</div>', unsafe_allow_html=True)

st.markdown("""
<span class="badge-pill">Claude 3.5 Sonnet</span>
<span class="badge-pill">Anthropic MCP SDK</span>
<span class="badge-pill">LangGraph StateGraph</span>
<span class="badge-pill">DuckDB / Snowflake</span>
<span class="badge-pill">Deterministic Guardrails</span>
""", unsafe_allow_html=True)
st.write("")

# Query Input & Example Buttons
st.markdown("#### 💬 Ask an Enterprise Warehouse Question:")

example_col1, example_col2, example_col3 = st.columns(3)
example_col4, example_col5, example_col6 = st.columns(3)

q_prompt = None
if example_col1.button("🚨 Find Leaked Leads (Score >= 80 in New)"):
    q_prompt = "Find all high-intent leads that leaked through our marketing pipeline without sales follow-up"
if example_col2.button("🏆 Top 5 Enterprise Accounts by ACV"):
    q_prompt = "What are our top 5 enterprise accounts by Annual Contract Value?"
if example_col3.button("📈 Campaign ROI & Cost Per MQL"):
    q_prompt = "Compare marketing campaign performance and calculate cost per MQL across channels"
if example_col4.button("📉 Churn Analysis by Account Tier"):
    q_prompt = "Analyze churned accounts and financial loss segmented by customer tier"
if example_col5.button("🔁 Trigger Reflection Loop (Auto-Repair)"):
    q_prompt = "Run a test error query to evaluate self-correction"
if example_col6.button("🛡️ Test Security Guardrail (DROP TABLE)"):
    q_prompt = "DROP TABLE accounts;"

user_query = st.text_input(
    "Natural Language Query",
    value=q_prompt if q_prompt else "Find all high-intent leads that leaked through our marketing pipeline without sales follow-up",
    label_visibility="collapsed"
)

run_button = st.button("🚀 Execute Autonomous Agent", type="primary")

if run_button or q_prompt:
    with st.spinner("Agent executing LangGraph State Machine (Discovery → Generation → MCP Execution → Reflection)..."):
        start_time = time.time()
        state = st.session_state.agent.run(user_query)
        st.session_state.last_state = state
        elapsed_sec = round(time.time() - start_time, 3)

# Display Results if state is available
if st.session_state.last_state:
    state = st.session_state.last_state
    
    st.write("")
    st.markdown("---")
    
    # 1. Executive Summary & KPIs
    st.markdown(state.final_answer)
    
    # 2. Results Table or Security Trace
    if state.execution_result and state.execution_result.get("success"):
        cols = state.execution_result.get("columns", [])
        rows = state.execution_result.get("rows", [])
        df = pd.DataFrame(rows, columns=cols)
        
        tab_data, tab_sql, tab_trace = st.tabs(["📊 Data Table & Metrics", "📝 Sandboxed SQL Query", "🔄 LangGraph Execution Trace"])
        
        with tab_data:
            st.dataframe(df, use_container_width=True)
            
            # Quick visual chart if numerical columns exist
            num_cols = df.select_dtypes(include=["number"]).columns.tolist()
            if num_cols and len(df) > 1:
                st.caption(f"Visual Breakdown ({num_cols[0]}):")
                first_str_col = df.select_dtypes(include=["object"]).columns.tolist()
                chart_df = df.set_index(first_str_col[0]) if first_str_col else df
                st.bar_chart(chart_df[num_cols[0]])
                
        with tab_sql:
            st.markdown(f"**Explanation:** {state.sql_explanation}")
            st.code(state.generated_sql, language="sql")
            st.caption(f"⏱️ Warehouse Query Latency: **{state.execution_result.get('execution_time_ms')} ms**")
            
        with tab_trace:
            st.markdown("#### Cyclical StateGraph Node Transitions:")
            for step in state.execution_trace:
                with st.expander(f"[{step['timestamp']}] {step['step']}", expanded=True):
                    st.write(step["detail"])
                    
            if state.reflection_count > 0:
                st.warning(f"🔁 Self-Correction Triggered: Completed **{state.reflection_count} reflection cycles** to autonomously recover from database errors.")
    else:
        st.error(f"🛑 Execution Intercepted: {state.error_message}")
        tab_sql, tab_trace = st.tabs(["📝 Blocked Candidate SQL", "🔄 LangGraph Audit Trace"])
        with tab_sql:
            st.code(state.generated_sql if state.generated_sql else "-- No SQL generated", language="sql")
        with tab_trace:
            st.markdown("#### Intercepted State Machine Trace:")
            for step in state.execution_trace:
                with st.expander(f"[{step['timestamp']}] {step['step']}", expanded=True):
                    st.write(step["detail"])
