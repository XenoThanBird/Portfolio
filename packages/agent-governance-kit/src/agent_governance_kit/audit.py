"""Append-only, hash-chained audit log.

Each record carries the SHA-256 hash of its own canonical content, which
includes the previous record's hash — so any mutation, deletion, or
insertion anywhere in the chain invalidates every hash from that point
forward. ``AuditLog.verify()`` walks the chain and reports the first
broken link.

Storage is JSONL: one canonical-JSON record per line, opened in append
mode only. The log never rewrites existing lines.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Union

from ._locking import interprocess_lock

GENESIS_HASH = "0" * 64


def _canonical(payload: Dict[str, Any]) -> str:
    """Deterministic JSON encoding used for hashing (sorted keys, no whitespace)."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class AuditRecord:
    """One immutable link in the audit chain."""

    index: int
    timestamp: str
    actor: str
    action: str
    payload: Dict[str, Any]
    prev_hash: str
    hash: str = field(default="")

    def core(self) -> Dict[str, Any]:
        """The hashed portion of the record (everything except its own hash)."""
        d = asdict(self)
        d.pop("hash")
        return d

    def compute_hash(self) -> str:
        return hashlib.sha256(_canonical(self.core()).encode("utf-8")).hexdigest()

    def sealed(self) -> "AuditRecord":
        """Return a copy with the hash field populated."""
        return AuditRecord(**{**self.core(), "hash": self.compute_hash()})


@dataclass(frozen=True)
class VerificationResult:
    """Outcome of a chain verification pass."""

    valid: bool
    records_checked: int
    first_broken_index: Optional[int] = None
    reason: Optional[str] = None


class AuditIntegrityError(RuntimeError):
    """Raised when an operation would extend a log whose chain is broken."""


class AuditLog:
    """Append-only JSONL audit log with SHA-256 hash chaining.

    A new instance pointed at an existing file resumes the chain from the
    last record. Appending to a log whose existing chain fails
    verification raises :class:`AuditIntegrityError` rather than silently
    burying the tampering under fresh valid records.
    """

    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._next_index = 0
        self._tail_hash = GENESIS_HASH
        if self.path.exists() and self.path.stat().st_size > 0:
            result = self.verify()
            if not result.valid:
                raise AuditIntegrityError(
                    f"existing audit log fails verification at record "
                    f"{result.first_broken_index}: {result.reason}"
                )
            last = None
            for last in self.iter_records():
                pass
            assert last is not None
            self._next_index = last.index + 1
            self._tail_hash = last.hash

    @classmethod
    def verify_file(cls, path: Union[str, Path]) -> VerificationResult:
        """Verify an arbitrary log file without constructing an appendable
        instance — the right tool for inspecting an untrusted or
        possibly-tampered log."""
        inspector = cls.__new__(cls)
        inspector.path = Path(path)
        return inspector.verify()

    def _lock_path(self) -> Path:
        return self.path.with_name(self.path.name + ".lock")

    def _read_tail(self) -> Tuple[int, str]:
        """Read (next_index, tail_hash) from the last line on disk.

        Called under the append lock so concurrent writers always chain
        onto the *current* tail, not a constructor-time snapshot.
        """
        if not self.path.exists() or self.path.stat().st_size == 0:
            return 0, GENESIS_HASH
        last: Optional[str] = None
        with open(self.path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            data = b""
            pos = size
            while pos > 0:
                step = min(4096, pos)
                pos -= step
                f.seek(pos)
                data = f.read(step) + data
                stripped = data.rstrip(b"\n")
                if b"\n" in stripped:
                    last = stripped[stripped.rfind(b"\n") + 1 :].decode("utf-8")
                    break
            if last is None:
                last = data.rstrip(b"\n").decode("utf-8")
        if not last:
            return 0, GENESIS_HASH
        try:
            record = AuditRecord(**json.loads(last))
        except (json.JSONDecodeError, TypeError) as exc:
            raise AuditIntegrityError(f"tail record is malformed: {exc}") from exc
        return record.index + 1, record.hash

    def append(self, actor: str, action: str, payload: Optional[Dict[str, Any]] = None) -> AuditRecord:
        """Append a record and return it (with its hash sealed).

        The read-current-tail → compose → write sequence runs under an
        interprocess lock, so multiple ``AuditLog`` instances (including
        in other processes) sharing one file always produce a single
        consistent chain rather than duplicate indices.
        """
        with interprocess_lock(self._lock_path()):
            next_index, tail_hash = self._read_tail()
            record = AuditRecord(
                index=next_index,
                timestamp=_utcnow(),
                actor=actor,
                action=action,
                payload=payload or {},
                prev_hash=tail_hash,
            ).sealed()
            with open(self.path, "a", encoding="utf-8", newline="\n") as f:
                f.write(_canonical({**record.core(), "hash": record.hash}) + "\n")
                f.flush()
                os.fsync(f.fileno())
            self._next_index = record.index + 1
            self._tail_hash = record.hash
        return record

    def iter_records(self) -> Iterator[AuditRecord]:
        """Yield records as stored, without validating them."""
        if not self.path.exists():
            return
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                yield AuditRecord(**data)

    def records(self) -> List[AuditRecord]:
        return list(self.iter_records())

    def verify(self) -> VerificationResult:
        """Walk the chain; report validity and the first broken link.

        Detects, in order of precedence at each position: malformed
        lines, index gaps, chain discontinuities (``prev_hash`` not
        matching the prior record's hash), and content tampering (stored
        hash not matching recomputed hash).
        """
        expected_prev = GENESIS_HASH
        checked = 0
        if not self.path.exists():
            return VerificationResult(valid=True, records_checked=0)
        with open(self.path, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    record = AuditRecord(**json.loads(line))
                except (json.JSONDecodeError, TypeError) as exc:
                    return VerificationResult(
                        valid=False,
                        records_checked=checked,
                        first_broken_index=checked,
                        reason=f"malformed record on line {lineno + 1}: {exc}",
                    )
                if record.index != checked:
                    return VerificationResult(
                        valid=False,
                        records_checked=checked,
                        first_broken_index=checked,
                        reason=f"index gap: expected {checked}, found {record.index}",
                    )
                if record.prev_hash != expected_prev:
                    return VerificationResult(
                        valid=False,
                        records_checked=checked,
                        first_broken_index=record.index,
                        reason="chain discontinuity: prev_hash does not match prior record's hash",
                    )
                if record.compute_hash() != record.hash:
                    return VerificationResult(
                        valid=False,
                        records_checked=checked,
                        first_broken_index=record.index,
                        reason="content tampering: stored hash does not match recomputed hash",
                    )
                expected_prev = record.hash
                checked += 1
        return VerificationResult(valid=True, records_checked=checked)
