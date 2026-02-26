"""
Threat Intelligence Honeypot — Session Logger

JSONL session logging: source IP, port, timestamp, payload bytes,
protocol, and geolocation stub. Each connection attempt is logged
as a single JSON line for efficient streaming analysis.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional


@dataclass
class SessionRecord:
    """A single honeypot session (connection attempt)."""
    session_id: str = ""
    timestamp: str = ""
    source_ip: str = ""
    source_port: int = 0
    dest_port: int = 0
    protocol: str = ""
    service: str = ""
    payload_preview: str = ""
    payload_bytes: int = 0
    duration_seconds: float = 0.0
    geo_country: str = ""
    geo_city: str = ""
    classification: str = ""  # scan, brute_force, exploit, unknown


class SessionLogger:
    """
    Append-only JSONL logger for honeypot sessions.

    Each session is written as a single line of JSON, enabling
    efficient streaming reads and analysis without loading the
    entire file into memory.
    """

    def __init__(
        self,
        log_dir: str = "honeypot_logs",
        max_payload_bytes: int = 4096,
        max_entries_per_file: int = 10000,
    ):
        self.log_dir = log_dir
        self.max_payload_bytes = max_payload_bytes
        self.max_entries_per_file = max_entries_per_file
        self._current_count = 0
        self._current_file = None

        os.makedirs(log_dir, exist_ok=True)

    def log_session(self, record: SessionRecord) -> None:
        """Append a session record to the current log file."""
        if not record.timestamp:
            record.timestamp = datetime.now(timezone.utc).isoformat()

        # Truncate payload if needed
        if len(record.payload_preview) > self.max_payload_bytes:
            record.payload_preview = record.payload_preview[
                : self.max_payload_bytes
            ]

        log_path = self._get_log_path()
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), default=str) + "\n")

        self._current_count += 1

    def read_sessions(
        self, log_file: str = None, limit: int = None
    ) -> list:
        """Read session records from a log file."""
        if log_file is None:
            log_file = self._get_log_path()

        if not os.path.exists(log_file):
            return []

        sessions = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    sessions.append(SessionRecord(**data))
                except (json.JSONDecodeError, TypeError):
                    continue
                if limit and len(sessions) >= limit:
                    break

        return sessions

    def read_all_sessions(self) -> list:
        """Read all sessions from all log files."""
        sessions = []
        if not os.path.isdir(self.log_dir):
            return sessions

        log_files = sorted([
            os.path.join(self.log_dir, f)
            for f in os.listdir(self.log_dir)
            if f.endswith(".jsonl")
        ])

        for log_file in log_files:
            sessions.extend(self.read_sessions(log_file))

        return sessions

    def get_stats(self) -> dict:
        """Get logging statistics."""
        log_files = []
        total_size = 0

        if os.path.isdir(self.log_dir):
            for f in os.listdir(self.log_dir):
                if f.endswith(".jsonl"):
                    path = os.path.join(self.log_dir, f)
                    log_files.append(f)
                    total_size += os.path.getsize(path)

        return {
            "log_dir": self.log_dir,
            "log_files": len(log_files),
            "total_size_bytes": total_size,
        }

    def _get_log_path(self) -> str:
        """Get the current log file path, rotating if needed."""
        if (
            self._current_file
            and self._current_count < self.max_entries_per_file
        ):
            return self._current_file

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_file = os.path.join(
            self.log_dir, f"sessions_{timestamp}.jsonl"
        )
        self._current_count = 0
        return self._current_file
