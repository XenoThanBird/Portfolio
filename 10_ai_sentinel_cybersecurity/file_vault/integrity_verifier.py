"""
Envelope Encryption File Vault — Integrity Verifier

HMAC-SHA256 verification of encrypted vault files — detects tampering
of ciphertext without requiring decryption.
"""

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class IntegrityResult:
    """Result of an integrity verification check."""
    vault_path: str = ""
    original_name: str = ""
    status: str = ""  # "verified", "tampered", "missing", "error"
    stored_hmac: str = ""
    computed_hmac: str = ""
    detail: str = ""
    checked_at: str = ""


class IntegrityVerifier:
    """
    HMAC-SHA256 integrity verification for vault files.

    Computes HMACs over the full vault file content (header + ciphertext)
    to detect any tampering of the encrypted data without needing to
    decrypt it.
    """

    def __init__(self, hmac_key: bytes, vault_dir: str = "vault_data"):
        self.hmac_key = hmac_key
        self.vault_dir = vault_dir
        self._hmac_store_path = os.path.join(vault_dir, "integrity.json")

    def sign_file(self, vault_path: str) -> str:
        """
        Compute and store an HMAC for a vault file.

        Returns the hex-encoded HMAC.
        """
        if not os.path.isfile(vault_path):
            raise FileNotFoundError(f"File not found: {vault_path}")

        file_hmac = self._compute_hmac(vault_path)

        # Store the HMAC
        store = self._load_store()
        store[os.path.basename(vault_path)] = {
            "hmac": file_hmac,
            "signed_at": datetime.now(timezone.utc).isoformat(),
            "file_size": os.path.getsize(vault_path),
        }
        self._save_store(store)

        return file_hmac

    def verify_file(self, vault_path: str) -> IntegrityResult:
        """
        Verify the integrity of a vault file against its stored HMAC.

        Returns an IntegrityResult with status: verified, tampered,
        missing, or error.
        """
        result = IntegrityResult(
            vault_path=vault_path,
            checked_at=datetime.now(timezone.utc).isoformat(),
        )

        # Extract original name from vault file header
        try:
            with open(vault_path, "rb") as f:
                header_line = f.readline()
                header = json.loads(header_line.decode("utf-8"))
                result.original_name = header.get("original_name", "")
        except Exception:
            result.original_name = os.path.basename(vault_path)

        # Check if file exists
        if not os.path.isfile(vault_path):
            result.status = "missing"
            result.detail = "Vault file not found on disk"
            return result

        # Look up stored HMAC
        store = self._load_store()
        filename = os.path.basename(vault_path)
        stored = store.get(filename)

        if not stored:
            result.status = "missing"
            result.detail = "No stored HMAC found — file not yet signed"
            return result

        result.stored_hmac = stored["hmac"]

        # Compute current HMAC
        try:
            result.computed_hmac = self._compute_hmac(vault_path)
        except Exception as e:
            result.status = "error"
            result.detail = f"Failed to compute HMAC: {e}"
            return result

        # Compare
        if hmac.compare_digest(result.stored_hmac, result.computed_hmac):
            result.status = "verified"
            result.detail = "File integrity confirmed — no tampering detected"
        else:
            result.status = "tampered"
            result.detail = (
                "INTEGRITY VIOLATION: File has been modified since signing"
            )

        return result

    def verify_all(self) -> list:
        """Verify all vault files that have stored HMACs."""
        store = self._load_store()
        results = []

        for filename in store:
            vault_path = os.path.join(self.vault_dir, filename)
            results.append(self.verify_file(vault_path))

        return results

    def resign_all(self) -> int:
        """Re-sign all vault files (e.g., after key rotation). Returns count."""
        count = 0
        if not os.path.isdir(self.vault_dir):
            return count

        for filename in os.listdir(self.vault_dir):
            if filename.endswith(".vault"):
                vault_path = os.path.join(self.vault_dir, filename)
                self.sign_file(vault_path)
                count += 1

        return count

    def _compute_hmac(self, file_path: str) -> str:
        """Compute HMAC-SHA256 of a file's contents."""
        h = hmac.new(self.hmac_key, digestmod=hashlib.sha256)
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()

    def _load_store(self) -> dict:
        """Load the HMAC store from disk."""
        if os.path.exists(self._hmac_store_path):
            with open(self._hmac_store_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save_store(self, store: dict) -> None:
        """Save the HMAC store to disk."""
        os.makedirs(self.vault_dir, exist_ok=True)
        with open(self._hmac_store_path, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=2)
