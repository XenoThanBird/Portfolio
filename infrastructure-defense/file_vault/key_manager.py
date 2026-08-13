"""
Envelope Encryption File Vault — Key Manager

Master key generation, storage, rotation (re-wrap all data keys with
new master), and key versioning. Follows the AWS KMS envelope
encryption pattern.
"""

import json
import os
import secrets
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes


@dataclass
class MasterKeyMetadata:
    """Metadata for a master key version."""
    version: int = 0
    created_at: str = ""
    key_id: str = ""
    algorithm: str = "AES-256-GCM"
    is_active: bool = True


@dataclass
class WrappedDataKey:
    """A data key encrypted (wrapped) by the master key."""
    wrapped_key: bytes = b""
    iv: bytes = b""
    master_key_version: int = 0
    created_at: str = ""


class KeyManager:
    """
    Manages master keys and data key wrapping for envelope encryption.

    Pattern:
    1. Master key encrypts/decrypts data keys (never touches plaintext data)
    2. Data keys encrypt/decrypt actual file content
    3. Key rotation re-wraps all data keys with a new master key
    """

    def __init__(
        self,
        key_dir: str = "vault_keys",
        kdf_iterations: int = 480000,
        salt_length: int = 16,
        data_key_length: int = 32,
        iv_length: int = 12,
        max_versions: int = 5,
    ):
        self.key_dir = key_dir
        self.kdf_iterations = kdf_iterations
        self.salt_length = salt_length
        self.data_key_length = data_key_length
        self.iv_length = iv_length
        self.max_versions = max_versions

        self._master_keys: dict = {}  # version -> key bytes
        self._metadata_file = os.path.join(key_dir, "key_metadata.json")

    def initialize(self, passphrase: str) -> MasterKeyMetadata:
        """
        Initialize the key store with a new master key derived from passphrase.

        The passphrase is used with PBKDF2 to derive the master key.
        The salt is stored alongside metadata for re-derivation.
        """
        os.makedirs(self.key_dir, exist_ok=True)

        metadata = self._load_metadata()
        version = len(metadata.get("versions", [])) + 1

        # Generate salt and derive master key
        salt = secrets.token_bytes(self.salt_length)
        master_key = self._derive_key(passphrase, salt)

        key_id = secrets.token_hex(8)
        key_meta = MasterKeyMetadata(
            version=version,
            created_at=datetime.now(timezone.utc).isoformat(),
            key_id=key_id,
            is_active=True,
        )

        # Deactivate previous versions
        if "versions" in metadata:
            for v in metadata["versions"]:
                v["is_active"] = False

        # Store salt and metadata (never the key itself)
        if "versions" not in metadata:
            metadata["versions"] = []

        metadata["versions"].append({
            **asdict(key_meta),
            "salt": salt.hex(),
        })
        metadata["active_version"] = version

        self._save_metadata(metadata)
        self._master_keys[version] = master_key

        # Prune old versions
        self._prune_old_versions(metadata)

        return key_meta

    def unlock(self, passphrase: str, version: int = None) -> bool:
        """
        Unlock a master key version by re-deriving from passphrase.

        If version is None, unlocks the active version.
        Returns True if successful.
        """
        metadata = self._load_metadata()
        if not metadata.get("versions"):
            return False

        if version is None:
            version = metadata.get("active_version", 1)

        version_data = None
        for v in metadata["versions"]:
            if v["version"] == version:
                version_data = v
                break

        if not version_data:
            return False

        salt = bytes.fromhex(version_data["salt"])
        master_key = self._derive_key(passphrase, salt)

        # Verify by checking if we can decrypt a test value
        if "verification_token" in version_data:
            try:
                token_data = bytes.fromhex(version_data["verification_token"])
                iv = token_data[: self.iv_length]
                ciphertext = token_data[self.iv_length:]
                aesgcm = AESGCM(master_key)
                aesgcm.decrypt(iv, ciphertext, None)
            except Exception:
                return False

        self._master_keys[version] = master_key

        # Store verification token on first unlock if not present
        if "verification_token" not in version_data:
            self._store_verification_token(version, master_key, metadata)

        return True

    def generate_data_key(self) -> tuple:
        """
        Generate a new random data key and return (plaintext_key, wrapped_key).

        The plaintext key is used to encrypt data. The wrapped key is stored
        alongside the encrypted data for later decryption.
        """
        metadata = self._load_metadata()
        active_version = metadata.get("active_version")
        if not active_version or active_version not in self._master_keys:
            raise RuntimeError(
                "No active master key — call initialize() or unlock() first"
            )

        master_key = self._master_keys[active_version]

        # Generate random data key
        data_key = secrets.token_bytes(self.data_key_length)

        # Wrap (encrypt) the data key with the master key
        iv = secrets.token_bytes(self.iv_length)
        aesgcm = AESGCM(master_key)
        wrapped = aesgcm.encrypt(iv, data_key, None)

        wrapped_data_key = WrappedDataKey(
            wrapped_key=wrapped,
            iv=iv,
            master_key_version=active_version,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        return data_key, wrapped_data_key

    def unwrap_data_key(self, wrapped: WrappedDataKey) -> bytes:
        """Unwrap (decrypt) a data key using the appropriate master key version."""
        version = wrapped.master_key_version
        if version not in self._master_keys:
            raise RuntimeError(
                f"Master key version {version} not unlocked — "
                f"call unlock() with the correct passphrase"
            )

        master_key = self._master_keys[version]
        aesgcm = AESGCM(master_key)
        data_key = aesgcm.decrypt(wrapped.iv, wrapped.wrapped_key, None)
        return data_key

    def rotate_master_key(self, old_passphrase: str, new_passphrase: str) -> tuple:
        """
        Rotate the master key: generate a new master key and return the
        old and new versions for re-wrapping data keys.

        Returns (old_version, new_version) for the caller to re-wrap.
        """
        metadata = self._load_metadata()
        old_version = metadata.get("active_version")

        # Ensure old key is unlocked
        if old_version not in self._master_keys:
            if not self.unlock(old_passphrase, old_version):
                raise RuntimeError("Cannot unlock current master key")

        # Create new master key
        new_meta = self.initialize(new_passphrase)

        return old_version, new_meta.version

    def rewrap_data_key(self, wrapped: WrappedDataKey) -> WrappedDataKey:
        """Re-wrap a data key with the current active master key."""
        # Unwrap with old master key
        data_key = self.unwrap_data_key(wrapped)

        # Get active master key
        metadata = self._load_metadata()
        active_version = metadata.get("active_version")
        if active_version not in self._master_keys:
            raise RuntimeError("Active master key not unlocked")

        master_key = self._master_keys[active_version]

        # Re-wrap with new master key
        iv = secrets.token_bytes(self.iv_length)
        aesgcm = AESGCM(master_key)
        new_wrapped = aesgcm.encrypt(iv, data_key, None)

        return WrappedDataKey(
            wrapped_key=new_wrapped,
            iv=iv,
            master_key_version=active_version,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

    def get_active_version(self) -> Optional[int]:
        """Get the active master key version number."""
        metadata = self._load_metadata()
        return metadata.get("active_version")

    def list_versions(self) -> list:
        """List all master key versions with metadata."""
        metadata = self._load_metadata()
        return [
            MasterKeyMetadata(
                version=v["version"],
                created_at=v["created_at"],
                key_id=v["key_id"],
                is_active=v.get("is_active", False),
            )
            for v in metadata.get("versions", [])
        ]

    def _derive_key(self, passphrase: str, salt: bytes) -> bytes:
        """Derive a master key from passphrase using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.data_key_length,
            salt=salt,
            iterations=self.kdf_iterations,
        )
        return kdf.derive(passphrase.encode("utf-8"))

    def _store_verification_token(
        self, version: int, master_key: bytes, metadata: dict
    ) -> None:
        """Store an encrypted verification token for passphrase checking."""
        iv = secrets.token_bytes(self.iv_length)
        aesgcm = AESGCM(master_key)
        token = aesgcm.encrypt(iv, b"vault_verification_v1", None)
        combined = iv + token

        for v in metadata["versions"]:
            if v["version"] == version:
                v["verification_token"] = combined.hex()
                break

        self._save_metadata(metadata)

    def _load_metadata(self) -> dict:
        """Load key metadata from disk."""
        if os.path.exists(self._metadata_file):
            with open(self._metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_metadata(self, metadata: dict) -> None:
        """Save key metadata to disk."""
        os.makedirs(self.key_dir, exist_ok=True)
        with open(self._metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

    def _prune_old_versions(self, metadata: dict) -> None:
        """Remove old inactive key versions beyond max_versions."""
        versions = metadata.get("versions", [])
        if len(versions) > self.max_versions:
            # Keep only the most recent max_versions
            metadata["versions"] = versions[-self.max_versions:]
            self._save_metadata(metadata)
