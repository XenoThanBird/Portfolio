"""
Application configuration using Pydantic BaseSettings.
Loads from environment variables and .env file.
"""

from pathlib import Path
from typing import Dict, List, Optional

import yaml
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://lifecycle:lifecycle@localhost:5432/lifecycle"

    # Auth
    SECRET_KEY: str = "demo-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    JWT_ALGORITHM: str = "HS256"

    # LLM Provider
    LLM_PROVIDER: str = "mock"  # openai | anthropic | mock
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS: int = 4000
    LLM_TEMPERATURE: float = 0.7

    # App
    APP_TITLE: str = "AI Solution Lifecycle Platform"
    APP_VERSION: str = "1.0.0"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


def load_scoring_config() -> Dict:
    """Load scoring weights and thresholds from config.yaml."""
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return _default_scoring_config()


def _default_scoring_config() -> Dict:
    """Fallback scoring config if config.yaml is missing."""
    return {
        "value_weights": {
            "financial_impact": 0.30,
            "operational_excellence": 0.20,
            "strategic_value": 0.15,
            "risk_mitigation": 0.15,
            "customer_impact": 0.10,
            "innovation_index": 0.10,
        },
        "readiness_weights": {
            "data_maturity": 0.35,
            "organizational_readiness": 0.35,
            "technical_capability": 0.30,
        },
        "risk_matrix": {
            "probability": {
                "Very Low": 0.1,
                "Low": 0.3,
                "Medium": 0.5,
                "High": 0.7,
                "Very High": 0.9,
            },
            "impact": {
                "Minimal": 1,
                "Low": 2,
                "Medium": 3,
                "High": 4,
                "Critical": 5,
            },
        },
        "action_matrix": {
            "90-100": {"classification": "Transformational", "action": "Full deployment", "investment": "$50M+"},
            "75-89": {"classification": "Strategic", "action": "Phased rollout", "investment": "$20-50M"},
            "60-74": {"classification": "Tactical", "action": "Pilot program", "investment": "$5-20M"},
            "45-59": {"classification": "Experimental", "action": "Limited POC", "investment": "$1-5M"},
            "0-44": {"classification": "Monitor", "action": "Research only", "investment": "<$1M"},
        },
        "data_maturity_levels": {
            1: {"name": "Fragmented", "ai_readiness": 0.20},
            2: {"name": "Connected", "ai_readiness": 0.40},
            3: {"name": "Unified", "ai_readiness": 0.60},
            4: {"name": "Intelligent", "ai_readiness": 0.80},
            5: {"name": "Autonomous", "ai_readiness": 0.95},
        },
    }


settings = Settings()
