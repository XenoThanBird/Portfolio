"""State machine tests: three outcomes, human-only startover."""

from __future__ import annotations

from typing import Dict, List, Tuple

import pytest

from agent_governance_kit import (
    GovernanceStateMachine,
    HumanWarrant,
    Initiator,
    InvalidTransitionError,
    Outcome,
    RunState,
    StartoverNotPermittedError,
)


def machine_at_checking() -> GovernanceStateMachine:
    m = GovernanceStateMachine()
    m.advance(RunState.DRAFTING)
    m.advance(RunState.CHECKING)
    return m


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
    def test_agent_cannot_startover(self) -> None:
        m = machine_at_checking()
        with pytest.raises(StartoverNotPermittedError):
            m.fail(Outcome.STARTOVER, reason="agent tries", initiated_by=Initiator.AGENT)
        assert m.state is RunState.CHECKING  # nothing moved

    def test_agent_cannot_startover_even_with_stolen_warrant(self) -> None:
        """Possessing a warrant is not enough — the initiator must be human."""
        m = machine_at_checking()
        warrant = HumanWarrant(approver="jordan", reason="premise invalid")
        with pytest.raises(StartoverNotPermittedError):
            m.fail(
                Outcome.STARTOVER,
                reason="agent with warrant",
                initiated_by=Initiator.AGENT,
                warrant=warrant,
            )

    def test_human_without_warrant_rejected(self) -> None:
        m = machine_at_checking()
        with pytest.raises(StartoverNotPermittedError):
            m.fail(Outcome.STARTOVER, reason="no warrant", initiated_by=Initiator.HUMAN)

    def test_warrant_requires_named_approver_and_reason(self) -> None:
        with pytest.raises(ValueError):
            HumanWarrant(approver="   ", reason="x")
        with pytest.raises(ValueError):
            HumanWarrant(approver="jordan", reason="")

    def test_warranted_human_startover_succeeds_and_can_restart(self) -> None:
        m = machine_at_checking()
        t = m.fail(
            Outcome.STARTOVER,
            reason="premise wrong",
            initiated_by=Initiator.HUMAN,
            warrant=HumanWarrant(approver="jordan", reason="scope changed"),
        )
        assert m.state is RunState.STARTED_OVER
        assert t.initiated_by is Initiator.HUMAN
        assert "jordan" in t.reason
        m.advance(RunState.RETRIEVING, reason="fresh premise")
        assert m.state is RunState.RETRIEVING


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

    def test_denied_startover_never_reaches_the_hook(self) -> None:
        events: List[Tuple[str, Dict[str, str]]] = []
        m = GovernanceStateMachine(audit_hook=lambda a, d: events.append((a, d)))
        m.advance(RunState.DRAFTING)
        m.advance(RunState.CHECKING)
        with pytest.raises(StartoverNotPermittedError):
            m.fail(Outcome.STARTOVER, reason="agent", initiated_by=Initiator.AGENT)
        assert len(events) == 2  # only the two legal advances
