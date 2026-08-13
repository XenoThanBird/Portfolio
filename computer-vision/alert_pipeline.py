"""
Alert Pipeline
--------------
Configurable alert/logging system with severity levels, cooldown logic,
and multi-channel output (console, file, webhook).

Integrates with the Vision Monitor and Anomaly Detector to provide
structured alerting without flooding downstream systems.
"""

import json
import logging
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class AlertLevel:
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

    _severity_order = {"INFO": 0, "WARNING": 1, "CRITICAL": 2}

    @classmethod
    def gte(cls, level: str, threshold: str) -> bool:
        return cls._severity_order.get(level, 0) >= cls._severity_order.get(threshold, 0)


class Alert:
    def __init__(self, level: str, source: str, message: str, metadata: Optional[dict] = None):
        self.timestamp = datetime.utcnow().isoformat()
        self.level = level
        self.source = source
        self.message = message
        self.metadata = metadata or {}

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "source": self.source,
            "message": self.message,
            "metadata": self.metadata,
        }

    def __repr__(self):
        return f"[{self.level}] {self.source}: {self.message}"


class AlertPipeline:
    """
    Multi-level alert system with cooldowns and structured logging.

    Config example (in config.yaml):
        alerts:
          min_level: WARNING
          cooldown_seconds: 60
          output_dir: logs/alerts
          webhook_url: null
    """

    def __init__(self, config: dict):
        alert_cfg = config.get("alerts", {})
        self.min_level = alert_cfg.get("min_level", AlertLevel.WARNING)
        self.cooldown_seconds = alert_cfg.get("cooldown_seconds", 60)

        self.output_dir = Path(alert_cfg.get("output_dir", "logs/alerts"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.alert_log = self.output_dir / "alerts.jsonl"
        self._last_fired: dict[str, float] = defaultdict(float)
        self._alert_counts: dict[str, int] = defaultdict(int)

    def _cooldown_key(self, alert: Alert) -> str:
        return f"{alert.source}:{alert.level}:{alert.message[:50]}"

    def _is_cooled_down(self, alert: Alert) -> bool:
        key = self._cooldown_key(alert)
        now = time.time()
        if now - self._last_fired[key] < self.cooldown_seconds:
            return False
        self._last_fired[key] = now
        return True

    def fire(self, level: str, source: str, message: str, metadata: Optional[dict] = None):
        if not AlertLevel.gte(level, self.min_level):
            return

        alert = Alert(level, source, message, metadata)

        if not self._is_cooled_down(alert):
            logger.debug("Alert suppressed (cooldown): %s", alert)
            return

        self._alert_counts[level] += 1
        self._write_log(alert)
        self._write_console(alert)

    def _write_log(self, alert: Alert):
        with open(self.alert_log, "a") as f:
            f.write(json.dumps(alert.to_dict()) + "\n")

    def _write_console(self, alert: Alert):
        if alert.level == AlertLevel.CRITICAL:
            logger.critical("%s", alert)
        elif alert.level == AlertLevel.WARNING:
            logger.warning("%s", alert)
        else:
            logger.info("%s", alert)

    def get_summary(self) -> dict:
        return {
            "total_alerts": sum(self._alert_counts.values()),
            "by_level": dict(self._alert_counts),
            "log_file": str(self.alert_log),
        }
