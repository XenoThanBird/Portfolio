"""
RAG Configuration
------------------
Centralized config management with YAML defaults and environment variable overrides.
"""

import os
from pathlib import Path

import yaml


DEFAULT_CONFIG = {
    "embedding": {
        "provider": "openai",
        "model_name": "text-embedding-3-large",
        "dimensions": 1536,
        "batch_size": 100,
    },
    "llm": {
        "provider": "openai",
        "model_name": "gpt-4o-mini",
        "temperature": 0.1,
    },
    "vector_store": {
        "provider": "faiss",
        "index_type": "flat",
        "dimension": 1536,
        "similarity_metric": "cosine",
        "storage_path": "./vector_store",
    },
    "retrieval": {
        "top_k": 5,
        "similarity_threshold": 0.7,
        "max_context_length": 4000,
        "strategy": "vector",
    },
    "tools": {
        "wikipedia_enabled": True,
        "arxiv_enabled": True,
        "max_results_per_tool": 5,
    },
    "observability": {
        "log_level": "INFO",
        "log_dir": "logs",
        "enable_tracing": False,
    },
}

# Maps environment variables to config paths
ENV_OVERRIDES = {
    "OPENAI_API_KEY": ("llm", "api_key"),
    "ANTHROPIC_API_KEY": ("llm", "api_key"),
    "RAG_EMBEDDING_MODEL": ("embedding", "model_name"),
    "RAG_LLM_MODEL": ("llm", "model_name"),
    "RAG_LLM_PROVIDER": ("llm", "provider"),
    "RAG_TOP_K": ("retrieval", "top_k"),
    "RAG_SIMILARITY_THRESHOLD": ("retrieval", "similarity_threshold"),
    "RAG_LOG_LEVEL": ("observability", "log_level"),
}


class Config:
    """Configuration manager with YAML + env var support."""

    def __init__(self, config_path: str = None):
        self._config = dict(DEFAULT_CONFIG)
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                file_config = yaml.safe_load(f) or {}
            self._deep_merge(self._config, file_config)
        self._apply_env_overrides()

    def get(self, *keys, default=None):
        val = self._config
        for key in keys:
            if isinstance(val, dict):
                val = val.get(key)
            else:
                return default
            if val is None:
                return default
        return val

    def _apply_env_overrides(self):
        for env_var, path in ENV_OVERRIDES.items():
            value = os.getenv(env_var)
            if value is not None:
                section = self._config.setdefault(path[0], {})
                # Type coercion for numeric values
                if env_var in ("RAG_TOP_K",):
                    value = int(value)
                elif env_var in ("RAG_SIMILARITY_THRESHOLD",):
                    value = float(value)
                section[path[1]] = value

    @staticmethod
    def _deep_merge(base: dict, override: dict):
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                Config._deep_merge(base[key], value)
            else:
                base[key] = value

    @classmethod
    def from_dict(cls, config_dict: dict) -> "Config":
        instance = cls()
        cls._deep_merge(instance._config, config_dict)
        return instance
