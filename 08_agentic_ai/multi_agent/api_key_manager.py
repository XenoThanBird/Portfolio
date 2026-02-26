"""
API Key Manager
----------------
Secure API key validation, rotation tracking, and usage logging.
No hardcoded keys — all values loaded from environment variables.
"""

import hashlib
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    Manages API keys from environment variables with usage tracking.

    Keys are never stored in plaintext in logs — only hashed prefixes
    are recorded for audit purposes.
    """

    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self._audit = audit_logger or AuditLogger()
        self._key_registry: Dict[str, Dict[str, Any]] = {}
        self._usage_counts: Dict[str, int] = {}

    def register_key(self, name: str, env_var: str, required: bool = True):
        """
        Register an API key by its environment variable name.

        Args:
            name: Friendly name (e.g., "openai", "anthropic")
            env_var: Environment variable to read (e.g., "OPENAI_API_KEY")
            required: Whether the key is mandatory for operation
        """
        value = os.getenv(env_var)
        self._key_registry[name] = {
            "env_var": env_var,
            "required": required,
            "present": value is not None and len(value) > 0,
            "hash_prefix": self._hash_prefix(value) if value else None,
            "registered_at": datetime.utcnow().isoformat(),
        }
        self._usage_counts[name] = 0

        if required and not value:
            logger.warning("Required API key '%s' (%s) is not set", name, env_var)

        self._audit.log("key_registered", {
            "key_name": name,
            "env_var": env_var,
            "present": self._key_registry[name]["present"],
            "required": required,
        })

    def get_key(self, name: str) -> Optional[str]:
        """Retrieve a key value and log the access."""
        reg = self._key_registry.get(name)
        if not reg:
            logger.warning("Key '%s' not registered", name)
            return None

        value = os.getenv(reg["env_var"])
        if value:
            self._usage_counts[name] = self._usage_counts.get(name, 0) + 1
            self._audit.log("key_accessed", {
                "key_name": name,
                "hash_prefix": reg["hash_prefix"],
                "usage_count": self._usage_counts[name],
            })
        return value

    def validate_all(self) -> Dict[str, bool]:
        """Check that all required keys are present."""
        results = {}
        for name, reg in self._key_registry.items():
            value = os.getenv(reg["env_var"])
            is_valid = value is not None and len(value) > 0
            results[name] = is_valid
            if reg["required"] and not is_valid:
                logger.error("MISSING required key: %s (%s)", name, reg["env_var"])
        return results

    def get_status(self) -> List[Dict[str, Any]]:
        """Return status of all registered keys (no values exposed)."""
        return [
            {
                "name": name,
                "env_var": reg["env_var"],
                "required": reg["required"],
                "present": os.getenv(reg["env_var"]) is not None,
                "usage_count": self._usage_counts.get(name, 0),
                "hash_prefix": reg.get("hash_prefix", "N/A"),
            }
            for name, reg in self._key_registry.items()
        ]

    @staticmethod
    def _hash_prefix(key: str) -> str:
        """Return a safe hash prefix for audit logging (never the full key)."""
        return hashlib.sha256(key.encode()).hexdigest()[:12]
