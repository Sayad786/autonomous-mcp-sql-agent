"""Command Line Interface (CLI) for Autonomous MCP SQL Agent.
Demonstrates LangGraph StateGraph execution, tool calls, and self-correction traces.
"""

import sys
from tabulate import tabulate

from src.agent_graph import AutonomousSQLAgent

def main():
    agent = AutonomousSQLAgent()

    queries = [
        "Find all high-intent leads that leaked through our marketing pipeline without sales follow-up",
        "What are our top 5 enterprise accounts by Annual Contract Value?",
        "Compare marketing campaign performance and calculate cost per MQL across channels"
    ]

    query = sys.argv[1] if len(sys.argv) > 1 else queries[0]

    print("\n" + "="*80)
    print("🚀 AUTONOMOUS DATABASE REASONING AGENT (MCP + LANGGRAPH)")
    print("="*80)
    print(f"📥 Query: {query}\n")

    state = agent.run(query)

    # 1. Print Execution Trace
    print("🔄 LANGGRAPH STATE MACHINE EXECUTION TRACE:")
    print("-" * 80)
    for t in state.execution_trace:
        print(f"[{t['timestamp']}] {t['step']:<22} | {t['detail']}")
    print("-" * 80)

    # 2. Print Generated SQL
    print("\n📝 GENERATED SQL (Sandboxed & Audited via MCP):")
    print(state.generated_sql)

    # 3. Print Results Table
    if state.execution_result and state.execution_result.get("success"):
        cols = state.execution_result.get("columns", [])
        rows = state.execution_result.get("rows", [])
        print(f"\n📊 QUERY RESULTS ({len(rows)} rows, {state.execution_result.get('execution_time_ms')} ms):")
        print(tabulate(rows[:10], headers=cols, tablefmt="fancy_grid"))

    # 4. Final Executive Answer
    print("\n" + "="*80)
    print(state.final_answer)
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
