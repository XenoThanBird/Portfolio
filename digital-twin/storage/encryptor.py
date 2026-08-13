"""
Encryption and data classification for privacy-sensitive data.
Implements Fernet (AES-256) encryption with sensitivity-based storage routing.
"""

import hashlib
import json
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Union

from cryptography.fernet import Fernet


class DataSensitivity(str, Enum):
    """Data sensitivity classification levels."""

    HIGH = "high"        # Private messages, financial records, credentials
    MEDIUM = "medium"    # Calendar events, location history, internal docs
    LOW = "low"          # General preferences, non-sensitive records
    PUBLIC = "public"    # Already-public information


class DataClassifier:
    """
    Classifies data by sensitivity level.
    Determines appropriate storage location and encryption requirements.
    """

    HIGH_SENSITIVITY_KEYWORDS = {
        "password", "ssn", "credit_card", "bank", "private_message",
        "dm", "financial", "salary", "income", "credential",
    }

    HIGH_SENSITIVITY_TYPES = {
        "financial_transaction",
        "private_message",
        "authentication_credential",
    }

    MEDIUM_SENSITIVITY_KEYWORDS = {
        "location", "calendar", "meeting", "email",
        "contact", "phone", "address",
    }

    @classmethod
    def classify(
        cls,
        data: Dict[str, Any],
        data_type: Optional[str] = None,
        source: Optional[str] = None,
    ) -> DataSensitivity:
        """
        Classify data based on content, type, and source.

        Args:
            data: The data to classify
            data_type: Optional explicit data type
            source: Optional source identifier

        Returns:
            DataSensitivity level
        """
        if data_type and data_type.lower() in cls.HIGH_SENSITIVITY_TYPES:
            return DataSensitivity.HIGH

        data_str = json.dumps(data).lower()

        if any(kw in data_str for kw in cls.HIGH_SENSITIVITY_KEYWORDS):
            return DataSensitivity.HIGH

        if any(kw in data_str for kw in cls.MEDIUM_SENSITIVITY_KEYWORDS):
            return DataSensitivity.MEDIUM

        if source:
            source_lower = source.lower()
            if "bank" in source_lower or "financial" in source_lower:
                return DataSensitivity.HIGH

        if data.get("is_public") or data.get("visibility") == "public":
            return DataSensitivity.PUBLIC

        return DataSensitivity.LOW

    @classmethod
    def should_encrypt(
        cls,
        sensitivity: DataSensitivity,
        encrypt_all: bool = False,
        encrypt_sensitive: bool = True,
    ) -> bool:
        """Determine if data should be encrypted based on sensitivity."""
        if encrypt_all:
            return True
        if encrypt_sensitive and sensitivity in (
            DataSensitivity.HIGH,
            DataSensitivity.MEDIUM,
        ):
            return True
        return False

    @classmethod
    def get_storage_location(
        cls,
        sensitivity: DataSensitivity,
        sensitive_location: str = "local",
    ) -> str:
        """
        Determine appropriate storage location based on sensitivity.

        Returns:
            Storage location identifier: 'local' or 'remote'
        """
        if sensitivity == DataSensitivity.HIGH:
            return sensitive_location
        elif sensitivity == DataSensitivity.MEDIUM:
            return "local"
        else:
            return "local"


class Encryptor:
    """
    Handles encryption and decryption of sensitive data.
    Uses Fernet (AES-256) for symmetric encryption.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryptor.

        Args:
            encryption_key: Base64-encoded Fernet key.
                            If None, generates a temporary key (dev only).
        """
        if encryption_key is None:
            encryption_key = Fernet.generate_key().decode()
            print(
                "WARNING: Generated temporary encryption key.\n"
                "Set ENCRYPTION_KEY in your .env file for persistence."
            )

        self.fernet = Fernet(
            encryption_key.encode()
            if isinstance(encryption_key, str)
            else encryption_key
        )

    def encrypt(self, data: Union[str, bytes, Dict]) -> bytes:
        """Encrypt data (string, bytes, or dict)."""
        if isinstance(data, dict):
            data = json.dumps(data)
        if isinstance(data, str):
            data = data.encode()
        return self.fernet.encrypt(data)

    def decrypt(self, encrypted_data: bytes, as_json: bool = False) -> Union[str, Dict]:
        """Decrypt data, optionally parsing as JSON."""
        decrypted = self.fernet.decrypt(encrypted_data).decode()
        if as_json:
            return json.loads(decrypted)
        return decrypted

    def encrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """Encrypt a file to disk."""
        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + ".encrypted")
        with open(input_path, "rb") as f:
            data = f.read()
        with open(output_path, "wb") as f:
            f.write(self.encrypt(data))
        return output_path

    def decrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """Decrypt a file from disk."""
        if output_path is None:
            if input_path.suffix == ".encrypted":
                output_path = input_path.with_suffix("")
            else:
                output_path = input_path.with_suffix(".decrypted")
        with open(input_path, "rb") as f:
            encrypted_data = f.read()
        decrypted = self.decrypt(encrypted_data)
        with open(output_path, "w") as f:
            f.write(decrypted)
        return output_path

    @staticmethod
    def hash_data(data: Union[str, bytes]) -> str:
        """Create SHA-256 hash of data for indexing without storing content."""
        if isinstance(data, str):
            data = data.encode()
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def generate_key() -> str:
        """Generate a new Fernet encryption key."""
        return Fernet.generate_key().decode()
