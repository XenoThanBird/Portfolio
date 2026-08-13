"""HITL gate tests, including cross-process resume semantics."""

from __future__ import annotations

import threading
import time
from pathlib import Path

import pytest

from agent_governance_kit import (
    AlreadyDecidedError,
    ApprovalStatus,
    ApprovalTimeoutError,
    HITLGate,
    UnknownApprovalError,
)


@pytest.fixture()
def gate(tmp_path: Path) -> HITLGate:
    return HITLGate(tmp_path / "approvals")


class TestLifecycle:
    def test_request_starts_pending(self, gate: HITLGate) -> None:
        approval = gate.request("deploy draft 7", {"run": "r-1"})
        assert approval.status is ApprovalStatus.PENDING
        assert gate.status(approval.id).status is ApprovalStatus.PENDING

    def test_approve_records_decider_and_note(self, gate: HITLGate) -> None:
        approval = gate.request("publish report")
        decided = gate.approve(approval.id, decided_by="jordan", note="LGTM")
        assert decided.status is ApprovalStatus.APPROVED
        assert decided.decided_by == "jordan"
        assert decided.note == "LGTM"
        assert decided.decided_at is not None

    def test_reject_flow(self, gate: HITLGate) -> None:
        approval = gate.request("delete records")
        decided = gate.reject(approval.id, decided_by="jordan", note="too risky")
        assert decided.status is ApprovalStatus.REJECTED

    def test_decisions_are_one_way(self, gate: HITLGate) -> None:
        approval = gate.request("x")
        gate.approve(approval.id, decided_by="jordan")
        with pytest.raises(AlreadyDecidedError):
            gate.reject(approval.id, decided_by="mallory")

    def test_unknown_id_raises(self, gate: HITLGate) -> None:
        with pytest.raises(UnknownApprovalError):
            gate.status("nope")

    def test_pending_lists_only_undecided(self, gate: HITLGate) -> None:
        a = gate.request("a")
        gate.request("b")
        gate.approve(a.id, decided_by="jordan")
        pending = gate.pending()
        assert [p.subject for p in pending] == ["b"]


class TestCrossProcessResume:
    def test_second_gate_instance_sees_and_decides_state(self, tmp_path: Path) -> None:
        """Simulates two processes sharing a store: the requester writes,
        a separate reviewer instance loads and decides, the requester
        observes the decision."""
        store = tmp_path / "approvals"
        requester = HITLGate(store)
        approval = requester.request("ship it", {"run": "r-9"})

        reviewer = HITLGate(store)  # fresh instance == fresh process
        assert reviewer.status(approval.id).subject == "ship it"
        reviewer.approve(approval.id, decided_by="jordan")

        assert requester.status(approval.id).status is ApprovalStatus.APPROVED

    def test_wait_blocks_until_other_instance_decides(self, tmp_path: Path) -> None:
        store = tmp_path / "approvals"
        requester = HITLGate(store)
        approval = requester.request("long-running gate")

        def decide_later() -> None:
            time.sleep(0.3)
            HITLGate(store).approve(approval.id, decided_by="jordan")

        t = threading.Thread(target=decide_later)
        t.start()
        decided = requester.wait(approval.id, timeout=5.0, poll_interval=0.05)
        t.join()
        assert decided.status is ApprovalStatus.APPROVED

    def test_wait_times_out_when_nobody_decides(self, gate: HITLGate) -> None:
        approval = gate.request("forgotten")
        with pytest.raises(ApprovalTimeoutError):
            gate.wait(approval.id, timeout=0.3, poll_interval=0.05)
