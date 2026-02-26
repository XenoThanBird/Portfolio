"""
Envelope Encryption File Vault — Core Vault

File vault with envelope encryption: generates per-file data keys,
encrypts data key with master key, stores encrypted data + wrapped
key together. Follows the AWS KMS envelope encryption pattern.
"""

import json
import os
import secrets
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from key_manager import KeyManager, WrappedDataKey


# Vault file format version
VAULT_FORMAT_VERSION = 1


@dataclass
class VaultEntry:
    """Metadata for a single encrypted file in the vault."""
    original_name: str = ""
    original_size: int = 0
    vault_path: str = ""
    encrypted_at: str = ""
    master_key_version: int = 0
    hmac: str = ""  # Set by integrity_verifier


class FileVault:
    """
    Envelope encryption file vault.

    Architecture:
    1. Each file gets a unique random data key (AES-256)
    2. Data key encrypts the file content (AES-256-GCM)
    3. Master key encrypts (wraps) the data key
    4. Vault file = wrapped data key + IV + encrypted content
    5. Key rotation re-wraps data keys without re-encrypting files
    """

    def __init__(
        self,
        key_manager: KeyManager,
        vault_dir: str = "vault_data",
        iv_length: int = 12,
        encrypted_extension: str = ".vault",
    ):
        self.key_manager = key_manager
        self.vault_dir = vault_dir
        self.iv_length = iv_length
        self.encrypted_extension = encrypted_extension
        self._manifest_path = os.path.join(vault_dir, "manifest.json")

    def encrypt_file(self, file_path: str) -> VaultEntry:
        """
        Encrypt a file using envelope encryption.

        1. Generate a unique data key
        2. Encrypt file content with data key (AES-256-GCM)
        3. Wrap data key with master key
        4. Store everything in a vault file
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        os.makedirs(self.vault_dir, exist_ok=True)

        # Read plaintext
        with open(file_path, "rb") as f:
            plaintext = f.read()

        # Generate unique data key for this file
        data_key, wrapped_data_key = self.key_manager.generate_data_key()

        # Encrypt content with data key
        iv = secrets.token_bytes(self.iv_length)
        aesgcm = AESGCM(data_key)
        ciphertext = aesgcm.encrypt(iv, plaintext, None)

        # Build vault file: JSON header + binary payload
        original_name = os.path.basename(file_path)
        vault_filename = f"{original_name}{self.encrypted_extension}"
        vault_path = os.path.join(self.vault_dir, vault_filename)

        header = {
            "format_version": VAULT_FORMAT_VERSION,
            "original_name": original_name,
            "original_size": len(plaintext),
            "encrypted_at": datetime.now(timezone.utc).isoformat(),
            "wrapped_key": wrapped_data_key.wrapped_key.hex(),
            "wrapped_key_iv": wrapped_data_key.iv.hex(),
            "master_key_version": wrapped_data_key.master_key_version,
            "content_iv": iv.hex(),
        }

        # Write vault file: JSON header (newline-terminated) + ciphertext
        header_bytes = json.dumps(header).encode("utf-8")
        with open(vault_path, "wb") as f:
            f.write(header_bytes)
            f.write(b"\n")
            f.write(ciphertext)

        entry = VaultEntry(
            original_name=original_name,
            original_size=len(plaintext),
            vault_path=vault_path,
            encrypted_at=header["encrypted_at"],
            master_key_version=wrapped_data_key.master_key_version,
        )

        # Update manifest
        self._update_manifest(entry)

        return entry

    def decrypt_file(self, vault_path: str, output_dir: str = None) -> str:
        """
        Decrypt a vault file back to its original content.

        1. Read vault file header and ciphertext
        2. Unwrap data key using master key
        3. Decrypt content with data key
        4. Write plaintext to output
        """
        if not os.path.isfile(vault_path):
            raise FileNotFoundError(f"Vault file not found: {vault_path}")

        # Read vault file
        with open(vault_path, "rb") as f:
            raw = f.read()

        # Split header from ciphertext
        newline_pos = raw.index(b"\n")
        header = json.loads(raw[:newline_pos].decode("utf-8"))
        ciphertext = raw[newline_pos + 1:]

        # Reconstruct wrapped data key
        wrapped = WrappedDataKey(
            wrapped_key=bytes.fromhex(header["wrapped_key"]),
            iv=bytes.fromhex(header["wrapped_key_iv"]),
            master_key_version=header["master_key_version"],
        )

        # Unwrap data key
        data_key = self.key_manager.unwrap_data_key(wrapped)

        # Decrypt content
        content_iv = bytes.fromhex(header["content_iv"])
        aesgcm = AESGCM(data_key)
        plaintext = aesgcm.decrypt(content_iv, ciphertext, None)

        # Write output
        if output_dir is None:
            output_dir = os.path.dirname(vault_path)

        original_name = header.get("original_name", "decrypted_file")
        output_path = os.path.join(output_dir, original_name)

        with open(output_path, "wb") as f:
            f.write(plaintext)

        return output_path

    def rotate_keys(self, old_passphrase: str, new_passphrase: str) -> int:
        """
        Rotate the master key and re-wrap all data keys.

        This does NOT re-encrypt the file contents — only the data keys
        are re-wrapped with the new master key. This is the efficiency
        advantage of envelope encryption.

        Returns the number of files re-wrapped.
        """
        old_version, new_version = self.key_manager.rotate_master_key(
            old_passphrase, new_passphrase
        )

        # Re-wrap all vault files
        count = 0
        vault_files = self._list_vault_files()

        for vault_path in vault_files:
            try:
                self._rewrap_vault_file(vault_path)
                count += 1
            except Exception as e:
                print(f"  Warning: Failed to re-wrap {vault_path}: {e}")

        return count

    def list_files(self) -> list:
        """List all files in the vault with metadata."""
        manifest = self._load_manifest()
        return manifest.get("entries", [])

    def _rewrap_vault_file(self, vault_path: str) -> None:
        """Re-wrap a single vault file's data key with the current master."""
        with open(vault_path, "rb") as f:
            raw = f.read()

        newline_pos = raw.index(b"\n")
        header = json.loads(raw[:newline_pos].decode("utf-8"))
        ciphertext = raw[newline_pos + 1:]

        # Reconstruct old wrapped key
        old_wrapped = WrappedDataKey(
            wrapped_key=bytes.fromhex(header["wrapped_key"]),
            iv=bytes.fromhex(header["wrapped_key_iv"]),
            master_key_version=header["master_key_version"],
        )

        # Re-wrap with current active master key
        new_wrapped = self.key_manager.rewrap_data_key(old_wrapped)

        # Update header
        header["wrapped_key"] = new_wrapped.wrapped_key.hex()
        header["wrapped_key_iv"] = new_wrapped.iv.hex()
        header["master_key_version"] = new_wrapped.master_key_version

        # Rewrite vault file
        header_bytes = json.dumps(header).encode("utf-8")
        with open(vault_path, "wb") as f:
            f.write(header_bytes)
            f.write(b"\n")
            f.write(ciphertext)

    def _list_vault_files(self) -> list:
        """List all vault files on disk."""
        if not os.path.isdir(self.vault_dir):
            return []
        return [
            os.path.join(self.vault_dir, f)
            for f in os.listdir(self.vault_dir)
            if f.endswith(self.encrypted_extension)
        ]

    def _update_manifest(self, entry: VaultEntry) -> None:
        """Update the vault manifest with a new entry."""
        manifest = self._load_manifest()
        if "entries" not in manifest:
            manifest["entries"] = []

        manifest["entries"].append(asdict(entry))
        manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
        manifest["total_files"] = len(manifest["entries"])

        with open(self._manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def _load_manifest(self) -> dict:
        """Load the vault manifest."""
        if os.path.exists(self._manifest_path):
            with open(self._manifest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
