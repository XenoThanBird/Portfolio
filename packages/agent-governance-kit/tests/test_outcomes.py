"""State machine tests: three outcomes, human-only startover backed by
a trusted approval boundary."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest

from agent_governance_kit import (
    GovernanceStateMachine,
    HITLGate,
    HumanWarrant,
    Initiator,
    InvalidTransitionError,
    Outcome,
    RunState,
    StartoverNotPermittedError,
    WarrantVerifier,
)


def machine_at_checking(
    verifier: Optional[WarrantVerifier] = None,
) -> GovernanceStateMachine:
    m = GovernanceStateMachine(warrant_verifier=verifier)
    m.advance(RunState.DRAFTING)
    m.advance(RunState.CHECKING)
    return m


def approved_startover(
    gate: HITLGate, approver: str = "jordan"
) -> HumanWarrant:
    """The legitimate path: a human approves a startover-scoped request."""
    approval = gate.request_startover("premise invalid, restart run")
    gate.approve(approval.id, decided_by=approver, note="scope changed")
    return HumanWarrant(
        approver=approver, reason="scope changed", approval_id=approval.id
    )


class TestForwardProgress:
    def test_happy_path(self) -> None:
        m = machine_at_checking()
        m.advance(RunState.AWAITING_APPROVAL)
        m.advance(RunState.APPROVED, reason="human approved")
        assert m.state is RunState.APPROVED
        assert [t.to_state for t in m.history] == [
            RunState.DRAFTING,
            RunState.CHECKING,
            RunState.AWAITING_APPROVAL,
            RunState.APPROVED,
        ]

    def test_illegal_skip_raises(self) -> None:
        m = GovernanceStateMachine()
        with pytest.raises(InvalidTransitionError):
            m.advance(RunState.APPROVED)

    def test_approved_is_terminal(self) -> None:
        m = machine_at_checking()
        m.advance(RunState.AWAITING_APPROVAL)
        m.advance(RunState.APPROVED)
        with pytest.raises(InvalidTransitionError):
            m.advance(RunState.DRAFTING)


class TestFailureOutcomes:
    def test_revise_returns_to_drafting(self) -> None:
        m = machine_at_checking()
        t = m.fail(Outcome.REVISE, reason="draft failed sentinel")
        assert m.state is RunState.DRAFTING
        assert t.outcome is Outcome.REVISE

    def test_repair_returns_to_retrieving(self) -> None:
        m = machine_at_checking()
        t = m.fail(Outcome.REPAIR, reason="evidence stale")
        assert m.state is RunState.RETRIEVING
        assert t.outcome is Outcome.REPAIR

    def test_outcomes_only_decidable_from_checking(self) -> None:
        m = GovernanceStateMachine()
        with pytest.raises(InvalidTransitionError):
            m.fail(Outcome.REVISE, reason="not checking yet")

    def test_revise_then_recheck_loop(self) -> None:
        m = machine_at_checking()
        m.fail(Outcome.REVISE, reason="first attempt bad")
        m.advance(RunState.CHECKING)
        m.advance(RunState.AWAITING_APPROVAL)
        assert m.state is RunState.AWAITING_APPROVAL


class TestStartoverIsHumanOnly:
    def test_agent_cannot_startover(self, tmp_path: Path) -> None:
        gate = HITLGate(tmp_path / "approvals")
        m = machine_at_checking(gate.startover_verifier())
        with pytest.raises(StartoverNotPermittedError):
            m.fail(Outcome.STARTOVER, reason="agent tries", initiated_by=Initiator.AGENT)
        assert m.state is RunState.CHECKING  # nothing moved

    def test_agent_cannot_startover_even_with_genuine_warrant(self, tmp_path: Path) -> None:
        """Possessing a real warrant is not enough — the initiator must be human."""
        gate = HITLGate(tmp_path / "approvals")
        m = machine_at_checking(gate.startover_verifier())
        warrant = approved_startover(gate)
        with pytest.raises(StartoverNotPermittedError):
            m.fail(
                Outcome.STARTOVER,
                reason="agent with warrant",
                initiated_by=Initiator.AGENT,
                warrant=warrant,
            )

    def test_human_without_warrant_rejected(self, tmp_path: Path) -> None:
        gate = HITLGate(tmp_path / "approvals")
        m = machine_at_checking(gate.startover_verifier())
        with pytest.raises(StartoverNotPermittedError):
            m.fail(Outcome.STARTOVER, reason="no warrant", initiated_by=Initiator.HUMAN)

    def test_warrant_requires_named_approver_reason_and_approval(self) -> None:
        with pytest.raises(ValueError):
            HumanWarrant(approver="   ", reason="x", approval_id="a")
        with pytest.raises(ValueError):
            HumanWarrant(approver="jordan", reason="", approval_id="a")
        with pytest.raises(ValueError):
            HumanWarrant(approver="jordan", reason="x", approval_id="  ")

    def test_no_verifier_means_startover_disabled(self) -> None:
        """Secure by default: a machine without a trusted approval
        boundary denies startover no matter what the caller asserts."""
        m = machine_at_checking(verifier=None)
        forged = HumanWarrant(approver="mallory", reason="trust me", approval_id="fake")
        with pytest.raises(StartoverNotPermittedError, match="no trusted approval boundary"):
            m.fail(
                Outcome.STARTOVER,
                reason="caller-asserted",
                initiated_by=Initiator.HUMAN,
                warrant=forged,
            )

    def test_forged_warrant_with_no_backing_approval_rejected(self, tmp_path: Path) -> None:
        """The P1 attack: agent code constructs HumanWarrant directly and
        claims Initiator.HUMAN. The verifier finds no approval record."""
        gate = HITLGate(tmp_path / "approvals")
        m = machine_at_checking(gate.startover_verifier())
        forged = HumanWarrant(approver="mallory", reason="fabricated", approval_id="deadbeef")
        with pytest.raises(StartoverNotPermittedError, match="no approval"):
            m.fail(
                Outcome.STARTOVER,
                reason="forged",
                initiated_by=Initiator.HUMAN,
                warrant=forged,
            )
        assert m.state is RunState.CHECKING

    def test_unrelated_approval_cannot_be_replayed_as_startover(self, tmp_path: Path) -> None:
        gate = HITLGate(tmp_path / "approvals")
        m = machine_at_checking(gate.startover_verifier())
        unrelated = gate.request("publish report")  # not startover-scoped
        gate.approve(unrelated.id, decided_by="jordan")
        warrant = HumanWarrant(approver="jordan", reason="reuse", approval_id=unrelated.id)
        with pytest.raises(StartoverNotPermittedError, match="not scoped to startover"):
            m.fail(Outcome.STARTOVER, reason="replay", initiated_by=Initiator.HUMAN, warrant=warrant)

    def test_pending_and_rejected_approvals_do_not_authorize(self, tmp_path: Path) -> None:
        gate = HITLGate(tmp_path / "approvals")
        m = machine_at_checking(gate.startover_verifier())
        pending = gate.request_startover("still waiting")
        warrant = HumanWarrant(approver="jordan", reason="early", approval_id=pending.id)
        with pytest.raises(StartoverNotPermittedError, match="pending"):
            m.fail(Outcome.STARTOVER, reason="early", initiated_by=Initiator.HUMAN, warrant=warrant)
        gate.reject(pending.id, decided_by="jordan", note="no")
        with pytest.raises(StartoverNotPermittedError, match="rejected"):
            m.fail(Outcome.STARTOVER, reason="denied", initiated_by=Initiator.HUMAN, warrant=warrant)

    def test_approver_must_match_recorded_decider(self, tmp_path: Path) -> None:
        gate = HITLGate(tmp_path / "approvals")
        m = machine_at_checking(gate.startover_verifier())
        approval = gate.request_startover("restart")
        gate.approve(approval.id, decided_by="jordan")
        warrant = HumanWarrant(approver="mallory", reason="stolen id", approval_id=approval.id)
        with pytest.raises(StartoverNotPermittedError, match="does not match"):
            m.fail(Outcome.STARTOVER, reason="mismatch", initiated_by=Initiator.HUMAN, warrant=warrant)

    def test_genuine_warrant_succeeds_and_is_single_use(self, tmp_path: Path) -> None:
        gate = HITLGate(tmp_path / "approvals")
        m = machine_at_checking(gate.startover_verifier())
        warrant = approved_startover(gate)
        t = m.fail(
            Outcome.STARTOVER,
            reason="premise wrong",
            initiated_by=Initiator.HUMAN,
            warrant=warrant,
        )
        assert m.state is RunState.STARTED_OVER
        assert t.initiated_by is Initiator.HUMAN
        assert "jordan" in t.reason and warrant.approval_id in t.reason
        m.advance(RunState.RETRIEVING, reason="fresh premise")
        m.advance(RunState.DRAFTING)
        m.advance(RunState.CHECKING)
        with pytest.raises(StartoverNotPermittedError, match="already used"):
            m.fail(Outcome.STARTOVER, reason="replay", initiated_by=Initiator.HUMAN, warrant=warrant)


class TestAuditHook:
    def test_every_transition_reaches_the_hook(self) -> None:
        events: List[Tuple[str, Dict[str, str]]] = []
        m = GovernanceStateMachine(audit_hook=lambda a, d: events.append((a, d)))
        m.advance(RunState.DRAFTING)
        m.advance(RunState.CHECKING)
        m.fail(Outcome.REVISE, reason="bad draft")
        assert len(events) == 3
        assert all(action == "state_transition" for action, _ in events)
        assert events[-1][1]["outcome"] == "revise"

    def test_denied_startover_is_audited_before_raising(self) -> None:
        """A denied attempt must leave evidence through the hook — the
        application should see what the machine refused to do."""
        events: List[Tuple[str, Dict[str, str]]] = []
        m = GovernanceStateMachine(audit_hook=lambda a, d: events.append((a, d)))
        m.advance(RunState.DRAFTING)
        m.advance(RunState.CHECKING)
        with pytest.raises(StartoverNotPermittedError):
            m.fail(Outcome.STARTOVER, reason="agent", initiated_by=Initiator.AGENT)
        denials = [(a, d) for a, d in events if a == "startover_denied"]
        assert len(denials) == 1
        assert "human-only" in denials[0][1]["detail"]
        # ...but no state transition was recorded for the denial
        transitions = [e for e in events if e[0] == "state_transition"]
        assert len(transitions) == 2
        assert m.state is RunState.CHECKING

    def test_hook_failure_prevents_state_commit(self) -> None:
        """If the audit hook cannot record the transition, the run must
        not advance: no divergence between state and evidence."""

        def failing_hook(action: str, detail: Dict[str, str]) -> None:
            raise OSError("disk full")

        m = GovernanceStateMachine(audit_hook=failing_hook)
        with pytest.raises(OSError, match="disk full"):
            m.advance(RunState.DRAFTING)
        assert m.state is RunState.RETRIEVING  # unchanged
        assert m.history == ()  # no transition recorded
