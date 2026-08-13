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


class TestConcurrentDecisions:
    def test_racing_reviewers_exactly_one_wins(self, tmp_path: Path) -> None:
        """Two reviewer instances decide the same request concurrently:
        exactly one decision succeeds, every other racer gets
        AlreadyDecidedError, and the stored file is valid JSON with the
        winner's decision."""
        store = tmp_path / "approvals"
        approval = HITLGate(store).request("contested decision")

        results: list = []
        barrier = threading.Barrier(8)

        def racer(n: int) -> None:
            gate = HITLGate(store)  # separate instance == separate process
            barrier.wait()
            try:
                if n % 2 == 0:
                    results.append(("approved", gate.approve(approval.id, decided_by=f"rev{n}")))
                else:
                    results.append(("rejected", gate.reject(approval.id, decided_by=f"rev{n}")))
            except AlreadyDecidedError:
                results.append(("lost", None))

        threads = [threading.Thread(target=racer, args=(i,)) for i in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        winners = [r for r in results if r[0] != "lost"]
        assert len(winners) == 1
        assert sum(1 for r in results if r[0] == "lost") == 7

        # Stored state parses cleanly and matches the winner.
        final = HITLGate(store).status(approval.id)
        assert final.status is not ApprovalStatus.PENDING
        assert final.status.value == winners[0][0]
        assert final.decided_by == winners[0][1].decided_by
