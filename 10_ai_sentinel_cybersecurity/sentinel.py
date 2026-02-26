"""
The Sentinel Script — File Integrity Monitor
----------------------------------------------
Automated file integrity monitoring for critical infrastructure.
Detects unauthorized changes via recursive hashing, baseline
comparison, and configurable alerting.

Usage:
    python sentinel.py --mode baseline       # Create initial baseline
    python sentinel.py --mode scan           # One-shot integrity check
    python sentinel.py --mode watch          # Continuous monitoring
    python sentinel.py --config custom.yaml  # Custom configuration
"""

import argparse
import hashlib
import logging
import os
import signal
import stat
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from alert_handler import AlertHandler
from baseline_manager import BaselineManager

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

logger = logging.getLogger("sentinel")


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class FileRecord:
    """Snapshot of a single file's integrity-relevant attributes."""
    path: str
    hash: str
    size: int
    permissions: str
    owner: Optional[str]
    group: Optional[str]
    modified_at: str
    scanned_at: str

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "FileRecord":
        return cls(**{k: d[k] for k in cls.__dataclass_fields__ if k in d})


@dataclass
class ChangeEvent:
    """A detected change between baseline and current state."""
    change_type: str       # added | modified | deleted | permissions_changed
    path: str
    severity: str          # CRITICAL | HIGH | MEDIUM | LOW
    details: dict
    detected_at: str

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------

class Sentinel:
    """Core file integrity monitoring engine."""

    def __init__(self, config: dict):
        watch_cfg = config.get("watch", {})
        scan_cfg = config.get("scanning", {})

        self.watch_paths: List[str] = watch_cfg.get("paths", [])
        self.exclude_patterns: List[str] = watch_cfg.get("exclude_patterns", [])
        self.follow_symlinks: bool = watch_cfg.get("follow_symlinks", False)
        self.max_file_size: int = watch_cfg.get("max_file_size_mb", 100) * 1024 * 1024

        self.hash_algorithm: str = scan_cfg.get("hash_algorithm", "sha256")
        self.track_permissions: bool = scan_cfg.get("track_permissions", True)
        self.scan_interval: int = scan_cfg.get("interval_seconds", 30)
        self.mode: str = scan_cfg.get("mode", "polling")

        self.severity_rules: dict = config.get("severity_rules", {})
        self._running: bool = False

    # --- Scanning ---

    def scan(self) -> Dict[str, FileRecord]:
        """Recursively scan all watch paths. Returns {path: FileRecord}."""
        all_files: Dict[str, FileRecord] = {}
        for watch_path in self.watch_paths:
            root = Path(watch_path)
            if not root.exists():
                logger.warning("Watch path does not exist: %s", watch_path)
                continue
            if root.is_file():
                record = self._scan_file(root)
                if record:
                    all_files[str(root)] = record
            else:
                all_files.update(self._scan_directory(root))
        return all_files

    def _scan_directory(self, root: Path) -> Dict[str, FileRecord]:
        """Walk a single directory tree, respecting exclude patterns."""
        files: Dict[str, FileRecord] = {}
        for dirpath, dirnames, filenames in os.walk(
            str(root), followlinks=self.follow_symlinks
        ):
            # Filter excluded directories in-place
            dirnames[:] = [
                d for d in dirnames
                if not self._is_excluded(os.path.join(dirpath, d))
            ]

            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if self._is_excluded(filepath):
                    continue
                record = self._scan_file(Path(filepath))
                if record:
                    files[filepath] = record

        return files

    def _scan_file(self, filepath: Path) -> Optional[FileRecord]:
        """Hash a single file and capture metadata."""
        try:
            file_stat = filepath.stat()

            if file_stat.st_size > self.max_file_size:
                logger.debug("Skipping large file: %s (%d bytes)", filepath, file_stat.st_size)
                return None

            file_hash = self._hash_file(filepath)
            if file_hash is None:
                return None

            perms, owner, group = self._get_file_metadata(filepath, file_stat)

            return FileRecord(
                path=str(filepath),
                hash=file_hash,
                size=file_stat.st_size,
                permissions=perms,
                owner=owner,
                group=group,
                modified_at=datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                scanned_at=datetime.utcnow().isoformat(),
            )
        except (OSError, PermissionError) as e:
            logger.debug("Cannot access %s: %s", filepath, e)
            return None

    def _is_excluded(self, path: str) -> bool:
        """Check path against all exclude patterns."""
        basename = os.path.basename(path)
        return any(
            fnmatch(path, pat) or fnmatch(basename, pat)
            for pat in self.exclude_patterns
        )

    def _hash_file(self, filepath: Path) -> Optional[str]:
        """Compute hash of file contents using configured algorithm."""
        try:
            h = hashlib.new(self.hash_algorithm)
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    h.update(chunk)
            return h.hexdigest()
        except (OSError, PermissionError) as e:
            logger.debug("Cannot hash %s: %s", filepath, e)
            return None

    def _get_file_metadata(self, filepath: Path, file_stat) -> tuple:
        """Extract permissions, owner, and group."""
        perms = stat.filemode(file_stat.st_mode)

        owner = None
        group = None
        if os.name != "nt":
            try:
                import pwd
                import grp
                owner = pwd.getpwuid(file_stat.st_uid).pw_name
                group = grp.getgrgid(file_stat.st_gid).gr_name
            except (KeyError, ImportError):
                owner = str(file_stat.st_uid)
                group = str(file_stat.st_gid)
        else:
            owner = str(file_stat.st_uid) if hasattr(file_stat, "st_uid") else None

        return perms, owner, group

    # --- Comparison ---

    def compare(
        self,
        baseline: Dict[str, dict],
        current: Dict[str, FileRecord],
    ) -> List[ChangeEvent]:
        """
        Diff baseline against current scan.

        Returns list of ChangeEvents for added, modified, deleted,
        and permission-changed files.
        """
        now = datetime.utcnow().isoformat()
        changes: List[ChangeEvent] = []

        baseline_paths = set(baseline.keys())
        current_paths = set(current.keys())

        # New files
        for path in sorted(current_paths - baseline_paths):
            changes.append(ChangeEvent(
                change_type="added",
                path=path,
                severity=self.classify_severity(path),
                details={"size": current[path].size},
                detected_at=now,
            ))

        # Deleted files
        for path in sorted(baseline_paths - current_paths):
            changes.append(ChangeEvent(
                change_type="deleted",
                path=path,
                severity=self.classify_severity(path),
                details={},
                detected_at=now,
            ))

        # Modified or permission-changed files
        for path in sorted(baseline_paths & current_paths):
            bl = baseline[path]
            cur = current[path]

            bl_hash = bl.get("hash") if isinstance(bl, dict) else bl.hash
            cur_hash = cur.hash if isinstance(cur, FileRecord) else cur.get("hash")

            bl_perms = bl.get("permissions") if isinstance(bl, dict) else bl.permissions
            cur_perms = cur.permissions if isinstance(cur, FileRecord) else cur.get("permissions")

            if bl_hash != cur_hash:
                changes.append(ChangeEvent(
                    change_type="modified",
                    path=path,
                    severity=self.classify_severity(path),
                    details={
                        "old_hash": bl_hash[:16] + "...",
                        "new_hash": cur_hash[:16] + "...",
                    },
                    detected_at=now,
                ))
            elif self.track_permissions and bl_perms != cur_perms:
                changes.append(ChangeEvent(
                    change_type="permissions_changed",
                    path=path,
                    severity=self.classify_severity(path),
                    details={
                        "old_permissions": bl_perms,
                        "new_permissions": cur_perms,
                    },
                    detected_at=now,
                ))

        return changes

    def classify_severity(self, filepath: str) -> str:
        """Map a file path to severity based on severity_rules patterns."""
        basename = os.path.basename(filepath)
        for level in ["critical", "high", "medium"]:
            patterns = self.severity_rules.get(level, [])
            for pattern in patterns:
                if fnmatch(basename, pattern) or fnmatch(filepath, pattern):
                    return level.upper()
        return "LOW"

    # --- Watch Mode ---

    def watch(self, baseline_manager: BaselineManager, alert_handler: AlertHandler):
        """Continuous monitoring loop."""
        self._running = True
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        if self.mode == "watchdog" and WATCHDOG_AVAILABLE:
            self._watch_watchdog(baseline_manager, alert_handler)
        else:
            if self.mode == "watchdog" and not WATCHDOG_AVAILABLE:
                logger.warning(
                    "watchdog not installed, falling back to polling. "
                    "Install with: pip install watchdog"
                )
            self._watch_polling(baseline_manager, alert_handler)

    def _watch_polling(self, baseline_manager: BaselineManager, alert_handler: AlertHandler):
        """Poll-based watch loop."""
        baseline = baseline_manager.load_latest()
        if not baseline:
            logger.error("No baseline found for watch mode.")
            return

        logger.info(
            "Polling every %ds across %d watch paths...",
            self.scan_interval, len(self.watch_paths),
        )

        while self._running:
            current = self.scan()
            changes = self.compare(baseline, current)
            for change in changes:
                alert_handler.fire(change)

            if changes:
                logger.info("Detected %d change(s)", len(changes))

            time.sleep(self.scan_interval)

    def _watch_watchdog(self, baseline_manager: BaselineManager, alert_handler: AlertHandler):
        """Watchdog-based filesystem event monitoring."""
        baseline = baseline_manager.load_latest()
        if not baseline:
            logger.error("No baseline found for watch mode.")
            return

        handler = _SentinelEventHandler(self, baseline, alert_handler)
        observer = Observer()

        for watch_path in self.watch_paths:
            if Path(watch_path).exists():
                observer.schedule(handler, watch_path, recursive=True)
                logger.info("Watching: %s", watch_path)

        observer.start()
        logger.info("Watchdog observer started.")

        try:
            while self._running:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()

    def _shutdown(self, signum, frame):
        """Graceful shutdown handler."""
        logger.info("Shutdown signal received (signal %d). Stopping...", signum)
        self._running = False


class _SentinelEventHandler(FileSystemEventHandler):
    """Bridges watchdog filesystem events into the Sentinel comparison pipeline."""

    def __init__(self, sentinel: Sentinel, baseline: dict, alert_handler: AlertHandler):
        super().__init__()
        self.sentinel = sentinel
        self.baseline = baseline
        self.alert_handler = alert_handler
        self._debounce: dict = {}
        self._debounce_window = 2.0  # seconds

    def on_any_event(self, event):
        if event.is_directory:
            return

        path = event.src_path
        if self.sentinel._is_excluded(path):
            return

        # Debounce rapid events on the same file
        now = time.time()
        if now - self._debounce.get(path, 0) < self._debounce_window:
            return
        self._debounce[path] = now

        # Re-scan the affected file and compare
        file_path = Path(path)
        if file_path.exists():
            record = self.sentinel._scan_file(file_path)
            if record:
                current = {path: record}
            else:
                current = {}
        else:
            current = {}

        bl_subset = {path: self.baseline[path]} if path in self.baseline else {}
        changes = self.sentinel.compare(bl_subset, current)

        # If file was added (not in baseline subset but exists now)
        if path not in self.baseline and current:
            changes.append(ChangeEvent(
                change_type="added",
                path=path,
                severity=self.sentinel.classify_severity(path),
                details={"size": record.size if record else 0},
                detected_at=datetime.utcnow().isoformat(),
            ))

        for change in changes:
            self.alert_handler.fire(change)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def load_config(path: str = "config.yaml") -> dict:
    """Load YAML configuration file."""
    with open(path) as f:
        return yaml.safe_load(f)


def setup_logging(config: dict):
    """Configure logging from config dict."""
    log_cfg = config.get("logging", {})
    log_dir = Path(log_cfg.get("output_dir", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, log_cfg.get("level", "INFO")),
        format=log_cfg.get(
            "console_format",
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        ),
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_dir / "sentinel.log"),
        ],
    )


def main():
    parser = argparse.ArgumentParser(
        description="The Sentinel Script - File Integrity Monitor"
    )
    parser.add_argument(
        "--mode",
        choices=["scan", "watch", "baseline"],
        default="scan",
        help="Operating mode (default: scan)",
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )
    parser.add_argument(
        "--baseline-name",
        default=None,
        help="Label for the baseline snapshot",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    setup_logging(config)

    sentinel = Sentinel(config)
    baseline_mgr = BaselineManager(config)
    alert_handler = AlertHandler(config)

    if args.mode == "baseline":
        current = sentinel.scan()
        path = baseline_mgr.save(current, name=args.baseline_name)
        logger.info("Baseline created: %d files -> %s", len(current), path)

    elif args.mode == "scan":
        baseline = baseline_mgr.load_latest()
        if not baseline:
            logger.error("No baseline found. Run with --mode baseline first.")
            sys.exit(1)
        current = sentinel.scan()
        changes = sentinel.compare(baseline, current)
        for change in changes:
            alert_handler.fire(change)
        alert_handler.print_summary()

    elif args.mode == "watch":
        baseline = baseline_mgr.load_latest()
        if not baseline:
            logger.error("No baseline found. Run with --mode baseline first.")
            sys.exit(1)
        logger.info("Starting watch mode (%s)...", sentinel.mode)
        sentinel.watch(baseline_mgr, alert_handler)


if __name__ == "__main__":
    main()
