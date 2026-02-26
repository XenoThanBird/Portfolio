"""
Configuration management using Pydantic BaseSettings.
Loads from environment variables and .env file with typed validation.
"""

from pathlib import Path
from typing import Literal, Optional
from functools import lru_cache

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Digital Twin system configuration.
    Environment variables override defaults; .env file is loaded automatically.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- general ---
    environment: Literal["development", "staging", "production"] = "development"
    log_level: str = "INFO"
    debug: bool = True

    # --- paths ---
    data_dir: Path = Field(default=Path("./data"))
    logs_dir: Path = Field(default=Path("./logs"))

    # --- storage ---
    vector_db_path: Path = Field(default=Path("./data/vector_db"))
    vector_db_collection_prefix: str = "dtwin_"

    metadata_db_type: Literal["sqlite", "postgresql"] = "sqlite"
    metadata_db_path: Path = Field(default=Path("./data/metadata.db"))

    graph_db_path: Path = Field(default=Path("./data/knowledge_graph.pkl"))

    # --- encryption ---
    encryption_key: Optional[str] = None
    encrypt_sensitive: bool = True
    encrypt_all: bool = False
    sensitive_data_location: Literal["local", "remote"] = "local"

    # --- embeddings ---
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 32

    # --- LLM (optional) ---
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # --- validators ---

    @validator("data_dir", "logs_dir", always=True)
    def create_directories(cls, v):
        """Ensure directories exist."""
        if v:
            Path(v).mkdir(parents=True, exist_ok=True)
        return v

    @property
    def database_url(self) -> str:
        if self.metadata_db_type == "sqlite":
            return f"sqlite:///{self.metadata_db_path}"
        raise ValueError("Configure PostgreSQL connection separately")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance (singleton per process)."""
    return Settings()
