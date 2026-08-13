"""
Audit Logger
-------------
Structured JSONL audit logging with automatic rotation and retention.
Designed for compliance-friendly record-keeping of agent actions,
API key usage, and system events.
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Append-only JSONL audit log with retention management.

    Each entry includes: timestamp, event type, actor, and payload.
    """

    def __init__(self, log_dir: str = "logs/audit", retention_days: int = 90):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self._log_file = self.log_dir / "audit.jsonl"

    def log(self, event_type: str, payload: Dict[str, Any], actor: Optional[str] = None):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "actor": actor or "system",
            "payload": payload,
        }

        with open(self._log_file, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def query(self, event_type: Optional[str] = None, limit: int = 50) -> list[Dict]:
        """Read recent audit entries, optionally filtered by event type."""
        if not self._log_file.exists():
            return []

        entries = []
        with open(self._log_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if event_type and entry.get("event_type") != event_type:
                        continue
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

        return entries[-limit:]

    def rotate(self):
        """Archive the current log and start a new one."""
        if not self._log_file.exists():
            return

        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        archive = self.log_dir / f"audit_{ts}.jsonl"
        self._log_file.rename(archive)
        logger.info("Rotated audit log to %s", archive)

    def enforce_retention(self):
        """Delete audit files older than retention_days."""
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        for path in self.log_dir.glob("audit_*.jsonl"):
            try:
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                if mtime < cutoff:
                    path.unlink()
                    logger.info("Deleted expired audit log: %s", path.name)
            except Exception as e:
                logger.warning("Failed to check/delete %s: %s", path, e)

    def get_summary(self) -> Dict[str, Any]:
        """Return a summary of audit log activity."""
        entries = self.query(limit=10000)
        event_counts: Dict[str, int] = {}
        for entry in entries:
            evt = entry.get("event_type", "unknown")
            event_counts[evt] = event_counts.get(evt, 0) + 1

        return {
            "total_entries": len(entries),
            "event_types": event_counts,
            "log_file": str(self._log_file),
            "retention_days": self.retention_days,
        }
