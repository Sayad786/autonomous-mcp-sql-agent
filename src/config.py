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
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    MODEL_NAME = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    MAX_TOKENS = 4096
    TEMPERATURE = 0.0  # Zero temperature for deterministic SQL generation
    
    # Guardrails & Operational Constraints
    MAX_ROW_LIMIT = 100
    QUERY_TIMEOUT_SECONDS = 10
    MAX_REFLECTION_RETRIES = 3
    
    @classmethod
    def is_anthropic_available(cls) -> bool:
        return bool(cls.ANTHROPIC_API_KEY and len(cls.ANTHROPIC_API_KEY.strip()) > 10)
