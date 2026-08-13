"""Audit log tests, including adversarial mid-chain tampering."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_governance_kit import (
    GENESIS_HASH,
    AuditIntegrityError,
    AuditLog,
    AuditRecord,
)


@pytest.fixture()
def log(tmp_path: Path) -> AuditLog:
    return AuditLog(tmp_path / "audit.jsonl")


def fill(log: AuditLog, n: int) -> None:
    for i in range(n):
        log.append(actor="agent", action=f"step_{i}", payload={"i": i})


class TestAppendAndChain:
    def test_genesis_prev_hash(self, log: AuditLog) -> None:
        record = log.append("agent", "start", {})
        assert record.prev_hash == GENESIS_HASH
        assert record.index == 0

    def test_chain_links_consecutive_records(self, log: AuditLog) -> None:
        first = log.append("agent", "one", {})
        second = log.append("agent", "two", {})
        assert second.prev_hash == first.hash
        assert second.index == 1

    def test_stored_hash_matches_recomputation(self, log: AuditLog) -> None:
        record = log.append("agent", "act", {"k": "v"})
        assert record.compute_hash() == record.hash

    def test_payload_roundtrip(self, log: AuditLog) -> None:
        log.append("scrubber", "redact", {"rule": "email", "count": 2})
        stored = log.records()[-1]
        assert stored.payload == {"rule": "email", "count": 2}
        assert stored.actor == "scrubber"

    def test_append_only_file_grows(self, log: AuditLog) -> None:
        fill(log, 3)
        assert len(log.path.read_text(encoding="utf-8").strip().splitlines()) == 3


class TestVerification:
    def test_empty_log_is_valid(self, log: AuditLog) -> None:
        result = log.verify()
        assert result.valid and result.records_checked == 0

    def test_intact_chain_verifies(self, log: AuditLog) -> None:
        fill(log, 10)
        result = log.verify()
        assert result.valid
        assert result.records_checked == 10
        assert result.first_broken_index is None

    def test_adversarial_mid_chain_payload_mutation(self, log: AuditLog) -> None:
        """Mutate record 5 of 10 on disk; verification must detect it and
        identify record 5 as the first broken link."""
        fill(log, 10)
        lines = log.path.read_text(encoding="utf-8").strip().splitlines()
        record = json.loads(lines[5])
        record["payload"]["i"] = 999_999  # the adversary edits history
        lines[5] = json.dumps(record, sort_keys=True, separators=(",", ":"))
        log.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        result = log.verify()
        assert not result.valid
        assert result.first_broken_index == 5
        assert result.reason is not None and "tampering" in result.reason

    def test_adversarial_mutation_with_recomputed_hash_breaks_next_link(
        self, log: AuditLog
    ) -> None:
        """A smarter adversary recomputes the mutated record's own hash.
        The record is now self-consistent — but record 6's prev_hash no
        longer matches, so the chain breaks at index 6."""
        fill(log, 10)
        lines = log.path.read_text(encoding="utf-8").strip().splitlines()
        data = json.loads(lines[5])
        data["payload"]["i"] = 999_999
        data.pop("hash")
        resealed = AuditRecord(**data).sealed()
        lines[5] = json.dumps(
            {**resealed.core(), "hash": resealed.hash},
            sort_keys=True,
            separators=(",", ":"),
        )
        log.path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        result = log.verify()
        assert not result.valid
        assert result.first_broken_index == 6
        assert result.reason is not None and "discontinuity" in result.reason

    def test_deleted_record_detected_as_gap_or_break(self, log: AuditLog) -> None:
        fill(log, 6)
        lines = log.path.read_text(encoding="utf-8").strip().splitlines()
        del lines[2]
        log.path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        result = log.verify()
        assert not result.valid
        assert result.first_broken_index == 2

    def test_malformed_line_detected(self, log: AuditLog) -> None:
        fill(log, 3)
        with open(log.path, "a", encoding="utf-8") as f:
            f.write("this is not json\n")
        result = log.verify()
        assert not result.valid
        assert result.first_broken_index == 3
        assert result.reason is not None and "malformed" in result.reason

    def test_truncation_from_end_is_still_a_valid_prefix(self, log: AuditLog) -> None:
        """Hash chains cannot detect pure tail truncation from the file
        alone — that requires an external anchor. Documented behavior."""
        fill(log, 5)
        lines = log.path.read_text(encoding="utf-8").strip().splitlines()
        log.path.write_text("\n".join(lines[:3]) + "\n", encoding="utf-8")
        result = log.verify()
        assert result.valid and result.records_checked == 3


class TestResume:
    def test_reopen_resumes_chain(self, tmp_path: Path) -> None:
        path = tmp_path / "audit.jsonl"
        first = AuditLog(path)
        fill(first, 4)
        tail = first.records()[-1].hash

        resumed = AuditLog(path)
        record = resumed.append("agent", "resumed", {})
        assert record.index == 4
        assert record.prev_hash == tail
        assert resumed.verify().valid

    def test_reopen_refuses_tampered_log(self, tmp_path: Path) -> None:
        path = tmp_path / "audit.jsonl"
        first = AuditLog(path)
        for i in range(3):
            first.append("agent", f"s{i}", {"i": i})
        lines = path.read_text(encoding="utf-8").strip().splitlines()
        data = json.loads(lines[1])
        data["actor"] = "mallory"
        lines[1] = json.dumps(data, sort_keys=True, separators=(",", ":"))
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        with pytest.raises(AuditIntegrityError):
            AuditLog(path)
