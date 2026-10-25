import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

class Config:
    """Enterprise Agent Configuration."""
    
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / "data"
    DB_PATH = DATA_DIR / "enterprise_warehouse.duckdb"
    
    # Anthropic Claude 3.5 Sonnet
    MODEL_NAME = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    MAX_TOKENS = 4096
    TEMPERATURE = 0.0  # Zero temperature for deterministic SQL generation
    
    # Guardrails & Operational Constraints
    MAX_ROW_LIMIT = 100
    QUERY_TIMEOUT_SECONDS = 10
    MAX_REFLECTION_RETRIES = 3
    
    @classmethod
    def get_anthropic_api_key(cls) -> str:
        key = os.getenv("ANTHROPIC_API_KEY", "")
        if not key:
            try:
                import streamlit as st
                if hasattr(st, "secrets") and "ANTHROPIC_API_KEY" in st.secrets:
                    key = st.secrets["ANTHROPIC_API_KEY"]
            except Exception:
                pass
        return key

    @classmethod
    def is_anthropic_available(cls) -> bool:
        key = cls.get_anthropic_api_key()
        return bool(key and len(key.strip()) > 10)
