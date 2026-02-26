"""
Envelope Encryption File Vault — CLI Interface

Commands: encrypt, decrypt, rotate-keys, verify, list
"""

import argparse
import getpass
import os
import sys

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


def get_passphrase(prompt: str = "Master passphrase: ") -> str:
    return getpass.getpass(prompt)


def cmd_encrypt(args):
    """Encrypt one or more files into the vault."""
    passphrase = get_passphrase()

    km = KeyManager(key_dir=args.key_dir)
    if km.get_active_version() is None:
        print(f"{CYAN}Initializing new vault...{RESET}")
        km.initialize(passphrase)
    else:
        if not km.unlock(passphrase):
            print(f"{RED}Invalid passphrase.{RESET}")
            sys.exit(1)

    vault = FileVault(km, vault_dir=args.vault_dir)
    hmac_key = passphrase.encode("utf-8")[:32].ljust(32, b"\x00")
    verifier = IntegrityVerifier(hmac_key, vault_dir=args.vault_dir)

    for file_path in args.files:
        try:
            entry = vault.encrypt_file(file_path)
            verifier.sign_file(entry.vault_path)
            print(
                f"  {GREEN}[OK]{RESET} {file_path} -> {entry.vault_path}"
            )
        except Exception as e:
            print(f"  {RED}[ERR]{RESET} {file_path}: {e}")


def cmd_decrypt(args):
    """Decrypt vault files back to plaintext."""
    passphrase = get_passphrase()

    km = KeyManager(key_dir=args.key_dir)
    if not km.unlock(passphrase):
        print(f"{RED}Invalid passphrase.{RESET}")
        sys.exit(1)

    vault = FileVault(km, vault_dir=args.vault_dir)
    output_dir = args.output or "."

    for vault_path in args.files:
        try:
            output = vault.decrypt_file(vault_path, output_dir=output_dir)
            print(f"  {GREEN}[OK]{RESET} {vault_path} -> {output}")
        except Exception as e:
            print(f"  {RED}[ERR]{RESET} {vault_path}: {e}")


def cmd_rotate(args):
    """Rotate the master key and re-wrap all data keys."""
    print(f"{CYAN}Master key rotation{RESET}")
    old_pass = get_passphrase("Current passphrase: ")
    new_pass = get_passphrase("New passphrase: ")
    confirm = get_passphrase("Confirm new passphrase: ")

    if new_pass != confirm:
        print(f"{RED}Passphrases do not match.{RESET}")
        sys.exit(1)

    km = KeyManager(key_dir=args.key_dir)
    if not km.unlock(old_pass):
        print(f"{RED}Invalid current passphrase.{RESET}")
        sys.exit(1)

    vault = FileVault(km, vault_dir=args.vault_dir)
    count = vault.rotate_keys(old_pass, new_pass)

    # Re-sign all files with new HMAC
    hmac_key = new_pass.encode("utf-8")[:32].ljust(32, b"\x00")
    verifier = IntegrityVerifier(hmac_key, vault_dir=args.vault_dir)
    verifier.resign_all()

    print(f"  {GREEN}Rotated master key, re-wrapped {count} file(s){RESET}")


def cmd_verify(args):
    """Verify integrity of vault files."""
    passphrase = get_passphrase()
    hmac_key = passphrase.encode("utf-8")[:32].ljust(32, b"\x00")

    verifier = IntegrityVerifier(hmac_key, vault_dir=args.vault_dir)

    if args.files:
        results = [verifier.verify_file(f) for f in args.files]
    else:
        results = verifier.verify_all()

    if not results:
        print(f"  {YELLOW}No vault files to verify.{RESET}")
        return

    for r in results:
        if r.status == "verified":
            icon = f"{GREEN}[OK]{RESET}"
        elif r.status == "tampered":
            icon = f"{RED}[TAMPERED]{RESET}"
        elif r.status == "missing":
            icon = f"{YELLOW}[MISSING]{RESET}"
        else:
            icon = f"{RED}[ERROR]{RESET}"

        name = r.original_name or os.path.basename(r.vault_path)
        print(f"  {icon} {name}: {r.detail}")


def cmd_list(args):
    """List all files in the vault."""
    km = KeyManager(key_dir=args.key_dir)
    vault = FileVault(km, vault_dir=args.vault_dir)
    entries = vault.list_files()

    if not entries:
        print(f"  {YELLOW}Vault is empty.{RESET}")
        return

    print(f"\n  {'Name':<30} {'Size':>10} {'Encrypted At':<25} {'Key Ver':>7}")
    print(f"  {'-'*30} {'-'*10} {'-'*25} {'-'*7}")
    for e in entries:
        name = e.get("original_name", "?")[:30]
        size = e.get("original_size", 0)
        enc_at = e.get("encrypted_at", "?")[:25]
        ver = e.get("master_key_version", "?")
        print(f"  {name:<30} {size:>10} {enc_at:<25} {ver:>7}")

    print(f"\n  Total: {len(entries)} file(s)")


def main():
    parser = argparse.ArgumentParser(
        description="Envelope Encryption File Vault",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--vault-dir", default="vault_data",
        help="Vault storage directory (default: vault_data)",
    )
    parser.add_argument(
        "--key-dir", default="vault_keys",
        help="Key storage directory (default: vault_keys)",
    )

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # encrypt
    p_enc = sub.add_parser("encrypt", help="Encrypt files into the vault")
    p_enc.add_argument("files", nargs="+", help="Files to encrypt")

    # decrypt
    p_dec = sub.add_parser("decrypt", help="Decrypt vault files")
    p_dec.add_argument("files", nargs="+", help="Vault files to decrypt")
    p_dec.add_argument("-o", "--output", help="Output directory")

    # rotate-keys
    sub.add_parser("rotate-keys", help="Rotate the master key")

    # verify
    p_ver = sub.add_parser("verify", help="Verify vault file integrity")
    p_ver.add_argument("files", nargs="*", help="Specific vault files (or all)")

    # list
    sub.add_parser("list", help="List all files in the vault")

    args = parser.parse_args()

    commands = {
        "encrypt": cmd_encrypt,
        "decrypt": cmd_decrypt,
        "rotate-keys": cmd_rotate,
        "verify": cmd_verify,
        "list": cmd_list,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
