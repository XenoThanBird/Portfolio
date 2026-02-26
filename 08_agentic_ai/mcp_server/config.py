"""
MCP Server Configuration
-------------------------
Immutable dataclass configuration loaded from environment variables.
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Server settings with sensible defaults."""
    server_name: str = os.getenv("MCP_SERVER_NAME", "mcp-template")
    user_agent: str = os.getenv("USER_AGENT", "MCPTemplate/1.0")
    timeout_seconds: float = float(os.getenv("TIMEOUT_SECONDS", "30"))
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    backoff_seconds: float = float(os.getenv("BACKOFF_SECONDS", "0.5"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
