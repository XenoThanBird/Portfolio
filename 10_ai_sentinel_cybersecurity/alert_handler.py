"""
Alert Handler — The Sentinel Script
-------------------------------------
Multi-channel alert routing with severity classification,
cooldown/dedup logic, and structured JSONL logging.

Channels: color-coded console, JSONL log file, optional webhook.
"""

import json
import logging
import time
import urllib.request
import urllib.error
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("sentinel.alerts")


class Severity:
    """Alert severity levels with ordering and display helpers."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

    _order = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}

    @classmethod
    def gte(cls, level: str, threshold: str) -> bool:
        """Return True if level >= threshold."""
        return cls._order.get(level, 0) >= cls._order.get(threshold, 0)

    @classmethod
    def color(cls, level: str) -> str:
        """ANSI color code for terminal output."""
        return {
            "CRITICAL": "\033[91m",   # red
            "HIGH": "\033[93m",       # yellow
            "MEDIUM": "\033[96m",     # cyan
            "LOW": "\033[92m",        # green
        }.get(level, "")

    RESET = "\033[0m"


class AlertHandler:
    """
    Routes file integrity change events to configured output channels.

    Supports:
    - Color-coded console output
    - JSONL append-only log file
    - Optional HTTP POST webhook
    - Per-event cooldown to prevent alert storms
    """

    def __init__(self, config: dict):
        alert_cfg = config.get("alerts", {})
        self.min_level: str = alert_cfg.get("min_level", Severity.LOW)
        self.cooldown_seconds: int = alert_cfg.get("cooldown_seconds", 30)

        self.output_dir = Path(alert_cfg.get("output_dir", "logs/alerts"))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.alert_log = self.output_dir / "alerts.jsonl"

        self.webhook_url: Optional[str] = alert_cfg.get("webhook_url")
        self.webhook_timeout: int = alert_cfg.get("webhook_timeout", 10)

        self._last_fired: dict = defaultdict(float)
        self._history: list = []
        self._counts: dict = defaultdict(int)

    def fire(self, change_event) -> bool:
        """
        Process a ChangeEvent. Returns True if the alert was dispatched.

        Skipped if severity is below min_level or event is in cooldown.
        """
        if not Severity.gte(change_event.severity, self.min_level):
            return False

        if not self._check_cooldown(change_event):
            logger.debug("Suppressed (cooldown): %s", change_event.path)
            return False

        alert_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "change_type": change_event.change_type,
            "path": change_event.path,
            "severity": change_event.severity,
            "details": change_event.details,
            "detected_at": change_event.detected_at,
        }

        self._history.append(alert_record)
        self._counts[change_event.severity] += 1

        self._to_console(change_event)
        self._to_log(alert_record)
        if self.webhook_url:
            self._to_webhook(alert_record)

        return True

    def _check_cooldown(self, event) -> bool:
        """Dedup key = change_type:path. Returns True if not in cooldown."""
        key = f"{event.change_type}:{event.path}"
        now = time.time()
        if now - self._last_fired[key] < self.cooldown_seconds:
            return False
        self._last_fired[key] = now
        return True

    def _to_console(self, event):
        """Color-coded console output with change icon."""
        c = Severity.color(event.severity)
        r = Severity.RESET
        icon = {
            "added": "+", "deleted": "-",
            "modified": "~", "permissions_changed": "!",
        }
        print(
            f"  {c}[{event.severity}]{r} "
            f"{icon.get(event.change_type, '?')} "
            f"{event.change_type.upper()}: {event.path}"
        )
        if event.details:
            for k, v in event.details.items():
                print(f"           {k}: {v}")

    def _to_log(self, record: dict):
        """Append alert to JSONL log file."""
        with open(self.alert_log, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _to_webhook(self, record: dict):
        """POST alert to webhook URL (best-effort, no retry)."""
        try:
            data = json.dumps(record).encode("utf-8")
            req = urllib.request.Request(
                self.webhook_url,
                data=data,
                headers={"Content-Type": "application/json"},
            )
            urllib.request.urlopen(req, timeout=self.webhook_timeout)
        except (urllib.error.URLError, OSError) as e:
            logger.warning("Webhook delivery failed: %s", e)

    def print_summary(self):
        """Print alert summary to console."""
        total = sum(self._counts.values())
        print(f"\n{'=' * 50}")
        print(f"  SENTINEL SCAN SUMMARY")
        print(f"{'=' * 50}")
        print(f"  Total alerts: {total}")
        for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            count = self._counts.get(level, 0)
            if count:
                c = Severity.color(level)
                print(f"  {c}{level}{Severity.RESET}: {count}")
        if total == 0:
            print("  No changes detected.")
        print(f"  Log: {self.alert_log}")
        print(f"{'=' * 50}\n")

    def get_history(self) -> list:
        """Return full alert history for this session."""
        return list(self._history)
