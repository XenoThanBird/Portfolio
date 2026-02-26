"""
Envelope Encryption File Vault — Example Demo

Demonstrates the full envelope encryption lifecycle:
1. Initialize vault with master key
2. Encrypt sample files with per-file data keys
3. Verify integrity via HMAC-SHA256
4. Rotate master key (re-wrap data keys)
5. Decrypt files
6. Tamper detection demonstration

Usage:
    python example.py
"""

import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from key_manager import KeyManager
from vault import FileVault
from integrity_verifier import IntegrityVerifier


# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(text: str) -> None:
    print(f"\n{BOLD}{CYAN}{'=' * 60}{RESET}")
    print(f"{BOLD}{CYAN}  {text}{RESET}")
    print(f"{BOLD}{CYAN}{'=' * 60}{RESET}\n")


def print_step(num: int, text: str) -> None:
    print(f"\n{BOLD}Step {num}: {text}{RESET}")
    print("-" * 40)


def main():
    print_header("Envelope Encryption File Vault — Demo")

    # Work in a temp directory for clean demo
    demo_dir = tempfile.mkdtemp(prefix="vault_demo_")
    vault_dir = os.path.join(demo_dir, "vault_data")
    key_dir = os.path.join(demo_dir, "vault_keys")
    sample_dir = os.path.join(demo_dir, "samples")
    decrypt_dir = os.path.join(demo_dir, "decrypted")
    os.makedirs(sample_dir)
    os.makedirs(decrypt_dir)

    passphrase = "demo-passphrase-not-for-production"

    try:
        # ── Step 1: Create sample files ──────────────────────────
        print_step(1, "Creating sample files")

        sample_files = {
            "financial_report.csv": (
                "date,revenue,expenses,profit\n"
                "2025-01,150000,120000,30000\n"
                "2025-02,165000,125000,40000\n"
                "2025-03,180000,130000,50000\n"
            ),
            "api_credentials.json": (
                '{\n'
                '  "api_key": "sk-demo-key-not-real-abc123",\n'
                '  "endpoint": "https://api.example.com/v2",\n'
                '  "environment": "staging"\n'
                '}\n'
            ),
            "patient_records.txt": (
                "Patient ID: P-1001\n"
                "Name: [REDACTED]\n"
                "Diagnosis: [REDACTED]\n"
                "Treatment: [REDACTED]\n"
                "Status: Active\n"
            ),
            "encryption_keys.pem": (
                "-----BEGIN DEMO CERTIFICATE-----\n"
                "MIIBkTCB+wIJANn3oX4VzHYeMA0GCSqGSIb3DQEBCwUAMBExDzANBgNV\n"
                "BAMMBmRlbW9DQTAeFw0yNTAxMDEwMDAwMDBaFw0yNjAxMDEwMDAwMDBa\n"
                "THIS-IS-A-DEMO-CERTIFICATE-NOT-REAL\n"
                "-----END DEMO CERTIFICATE-----\n"
            ),
        }

        for filename, content in sample_files.items():
            path = os.path.join(sample_dir, filename)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"  Created: {filename} ({len(content)} bytes)")

        # ── Step 2: Initialize vault ─────────────────────────────
        print_step(2, "Initializing vault with master key")

        km = KeyManager(key_dir=key_dir)
        meta = km.initialize(passphrase)
        print(f"  Master key version: {meta.version}")
        print(f"  Key ID:             {meta.key_id}")
        print(f"  Algorithm:          {meta.algorithm}")
        print(f"  {GREEN}Vault initialized{RESET}")

        vault = FileVault(km, vault_dir=vault_dir)

        # Set up integrity verifier
        hmac_key = passphrase.encode("utf-8")[:32].ljust(32, b"\x00")
        verifier = IntegrityVerifier(hmac_key, vault_dir=vault_dir)

        # ── Step 3: Encrypt files ────────────────────────────────
        print_step(3, "Encrypting files with envelope encryption")

        entries = []
        for filename in sample_files:
            file_path = os.path.join(sample_dir, filename)
            entry = vault.encrypt_file(file_path)
            verifier.sign_file(entry.vault_path)
            entries.append(entry)
            print(
                f"  {GREEN}[ENCRYPTED]{RESET} {filename} "
                f"-> {os.path.basename(entry.vault_path)} "
                f"(key v{entry.master_key_version})"
            )

        print(f"\n  Each file encrypted with a unique data key")
        print(f"  Data keys wrapped by master key v{meta.version}")

        # ── Step 4: Verify integrity ─────────────────────────────
        print_step(4, "Verifying file integrity (HMAC-SHA256)")

        results = verifier.verify_all()
        for r in results:
            if r.status == "verified":
                print(f"  {GREEN}[VERIFIED]{RESET} {r.original_name}")
            else:
                print(f"  {RED}[{r.status.upper()}]{RESET} {r.original_name}")

        # ── Step 5: Rotate master key ────────────────────────────
        print_step(5, "Rotating master key")

        new_passphrase = "rotated-passphrase-also-demo"
        count = vault.rotate_keys(passphrase, new_passphrase)

        # Re-sign with new HMAC key
        new_hmac_key = new_passphrase.encode("utf-8")[:32].ljust(32, b"\x00")
        new_verifier = IntegrityVerifier(new_hmac_key, vault_dir=vault_dir)
        new_verifier.resign_all()

        versions = km.list_versions()
        print(f"  {GREEN}Master key rotated{RESET}")
        print(f"  Re-wrapped {count} data key(s)")
        print(f"  Key versions: {[v.version for v in versions]}")
        print(f"  Active version: {km.get_active_version()}")
        print(f"  Note: File contents NOT re-encrypted (only keys re-wrapped)")

        # ── Step 6: Decrypt with rotated key ─────────────────────
        print_step(6, "Decrypting files with rotated key")

        # Unlock with new passphrase
        km2 = KeyManager(key_dir=key_dir)
        km2.unlock(new_passphrase)
        vault2 = FileVault(km2, vault_dir=vault_dir)

        for entry in entries:
            output = vault2.decrypt_file(entry.vault_path, decrypt_dir)
            # Verify content matches original
            original = os.path.join(sample_dir, entry.original_name)
            with open(original, "r") as f1, open(output, "r") as f2:
                match = f1.read() == f2.read()
            status = f"{GREEN}[MATCH]{RESET}" if match else f"{RED}[MISMATCH]{RESET}"
            print(f"  {status} {entry.original_name}")

        # ── Step 7: Tamper detection ─────────────────────────────
        print_step(7, "Tamper detection demonstration")

        # Pick the first vault file and tamper with it
        tamper_target = entries[0].vault_path
        tamper_name = entries[0].original_name
        print(f"  Tampering with: {tamper_name}")

        # Read, modify a byte, write back
        with open(tamper_target, "rb") as f:
            content = bytearray(f.read())
        content[-1] = (content[-1] + 1) % 256  # Flip last byte
        with open(tamper_target, "wb") as f:
            f.write(content)

        # Verify — should detect tampering
        result = new_verifier.verify_file(tamper_target)
        if result.status == "tampered":
            print(f"  {RED}[TAMPERED]{RESET} {result.detail}")
            print(f"  {GREEN}Tamper detection working correctly!{RESET}")
        else:
            print(f"  {YELLOW}[{result.status}]{RESET} {result.detail}")

        # Verify remaining files — should still be clean
        print(f"\n  Verifying remaining files:")
        for entry in entries[1:]:
            r = new_verifier.verify_file(entry.vault_path)
            if r.status == "verified":
                print(f"  {GREEN}[VERIFIED]{RESET} {entry.original_name}")
            else:
                print(f"  {RED}[{r.status.upper()}]{RESET} {entry.original_name}")

        # ── Step 8: List vault contents ──────────────────────────
        print_step(8, "Vault inventory")
        files = vault2.list_files()
        print(f"\n  {'Name':<30} {'Size':>8} {'Key Ver':>7}")
        print(f"  {'-'*30} {'-'*8} {'-'*7}")
        for e in files:
            print(
                f"  {e['original_name']:<30} "
                f"{e['original_size']:>8} "
                f"v{e['master_key_version']:>6}"
            )

    finally:
        # ── Cleanup ──────────────────────────────────────────────
        print_header("Cleanup")
        shutil.rmtree(demo_dir, ignore_errors=True)
        print(f"  {GREEN}Temporary demo files removed{RESET}")

    print(f"\n{BOLD}Demo complete.{RESET}\n")


if __name__ == "__main__":
    main()
