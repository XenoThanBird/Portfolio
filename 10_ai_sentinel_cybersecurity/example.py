"""
The Sentinel Script — Interactive Demo
-----------------------------------------
Self-contained demonstration that:
1. Creates a temporary directory with sample files
2. Establishes a baseline
3. Simulates unauthorized changes (add, modify, delete, permissions)
4. Runs an integrity scan and shows detections
5. Cleans up after itself

Usage:
    python example.py
"""

import os
import shutil
import stat
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from sentinel import Sentinel, load_config, setup_logging
from alert_handler import AlertHandler
from baseline_manager import BaselineManager


def _header(title: str):
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}\n")


def run_demo():
    """Full FIM demonstration with temporary files."""

    _header("THE SENTINEL SCRIPT — File Integrity Monitor Demo")

    # ---------------------------------------------------------------
    # Step 1: Create simulated file system
    # ---------------------------------------------------------------
    _header("Step 1: Creating Simulated File System")

    demo_dir = Path(tempfile.mkdtemp(prefix="sentinel_demo_"))
    print(f"  Demo directory: {demo_dir}")

    sample_files = {
        "config/app.conf":      "database_host=localhost\nport=5432\n",
        "config/auth.yaml":     "auth:\n  method: oauth2\n  provider: internal\n",
        "scripts/deploy.sh":    "#!/bin/bash\necho 'Deploying application...'\n",
        "scripts/backup.py":    "import shutil\n# automated backup logic\n",
        "data/users.csv":       "id,name,email\n1,Alice,alice@example.com\n2,Bob,bob@example.com\n",
        "data/settings.json":   '{"theme": "dark", "language": "en"}\n',
        "certs/server.pem":     "-----BEGIN CERTIFICATE-----\nDEMO_CERT_DATA\n-----END CERTIFICATE-----\n",
        "web/index.html":       "<html><body><h1>Welcome</h1></body></html>\n",
        "web/style.css":        "body { margin: 0; padding: 0; }\n",
        "README.md":            "# Demo Application\nSample project for FIM testing.\n",
    }

    for rel_path, content in sample_files.items():
        fp = demo_dir / rel_path
        fp.parent.mkdir(parents=True, exist_ok=True)
        fp.write_text(content)
        print(f"    Created: {rel_path}")

    print(f"\n  Total files: {len(sample_files)}")

    # ---------------------------------------------------------------
    # Step 2: Build demo configuration
    # ---------------------------------------------------------------
    demo_config = {
        "watch": {
            "paths": [str(demo_dir)],
            "exclude_patterns": ["*.pyc", "__pycache__/**"],
            "max_file_size_mb": 100,
        },
        "scanning": {
            "mode": "polling",
            "interval_seconds": 5,
            "hash_algorithm": "sha256",
            "track_permissions": True,
        },
        "baseline": {
            "storage_path": str(demo_dir / ".sentinel_baselines"),
            "auto_backup": True,
            "max_versions": 5,
        },
        "severity_rules": {
            "critical": ["*.pem", "*.key", "*.conf"],
            "high": ["*.py", "*.sh"],
            "medium": ["*.json", "*.yaml", "*.yml", "*.csv"],
        },
        "alerts": {
            "min_level": "LOW",
            "cooldown_seconds": 0,
            "output_dir": str(demo_dir / ".sentinel_logs"),
        },
        "logging": {
            "level": "WARNING",
            "output_dir": str(demo_dir / ".sentinel_logs"),
        },
    }

    # ---------------------------------------------------------------
    # Step 3: Establish baseline
    # ---------------------------------------------------------------
    _header("Step 2: Establishing Baseline")

    sentinel = Sentinel(demo_config)
    baseline_mgr = BaselineManager(demo_config)
    alert_handler = AlertHandler(demo_config)

    current = sentinel.scan()
    baseline_mgr.save(current, name="initial")
    print(f"  Baseline established: {len(current)} files indexed")
    print(f"  Hash algorithm: SHA-256\n")

    for i, (path, record) in enumerate(list(current.items())[:3]):
        try:
            rel = Path(path).relative_to(demo_dir)
        except ValueError:
            rel = path
        print(f"    {rel}: {record.hash[:16]}...")

    if len(current) > 3:
        print(f"    ... and {len(current) - 3} more")

    # ---------------------------------------------------------------
    # Step 4: Simulate unauthorized changes
    # ---------------------------------------------------------------
    _header("Step 3: Simulating Unauthorized Changes")

    # 4a. Modify a config file (CRITICAL)
    target = demo_dir / "config" / "app.conf"
    target.write_text("database_host=evil-server.attacker.com\nport=5432\n")
    print(f"  [~] Modified: config/app.conf (database host changed)")

    # 4b. Add a suspicious new script (HIGH)
    backdoor = demo_dir / "scripts" / "reverse_shell.sh"
    backdoor.write_text("#!/bin/bash\n# suspicious reverse shell script\n")
    print(f"  [+] Added:    scripts/reverse_shell.sh (suspicious script)")

    # 4c. Delete a certificate (CRITICAL)
    cert = demo_dir / "certs" / "server.pem"
    cert.unlink()
    print(f"  [-] Deleted:  certs/server.pem (certificate removed)")

    # 4d. Modify data file (MEDIUM)
    data_file = demo_dir / "data" / "users.csv"
    data_file.write_text(
        "id,name,email\n"
        "1,Alice,alice@example.com\n"
        "2,Bob,bob@example.com\n"
        "999,Intruder,hacker@evil.com\n"
    )
    print(f"  [~] Modified: data/users.csv (unauthorized user added)")

    # 4e. Permission change (Unix only)
    changes_count = 4
    if os.name != "nt":
        script = demo_dir / "scripts" / "deploy.sh"
        os.chmod(script, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        print(f"  [!] Perms:    scripts/deploy.sh (changed to 0o777)")
        changes_count = 5

    print(f"\n  Total simulated changes: {changes_count}")

    # ---------------------------------------------------------------
    # Step 5: Run integrity scan
    # ---------------------------------------------------------------
    _header("Step 4: Running Integrity Scan")

    baseline_data = baseline_mgr.load_latest()
    current = sentinel.scan()

    print(f"  Scanning {len(current)} files against baseline...\n")

    changes = sentinel.compare(baseline_data, current)
    for change in changes:
        alert_handler.fire(change)

    alert_handler.print_summary()

    # ---------------------------------------------------------------
    # Step 6: Show baseline report
    # ---------------------------------------------------------------
    _header("Step 5: Baseline Report")
    print(baseline_mgr.export_report())

    # ---------------------------------------------------------------
    # Step 7: Cleanup
    # ---------------------------------------------------------------
    _header("Cleanup")
    shutil.rmtree(demo_dir)
    print(f"  Removed demo directory: {demo_dir}")
    print(f"\n  Demo complete. No files remain.\n")


if __name__ == "__main__":
    run_demo()
