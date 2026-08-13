"""Failure semantics as a first-class state machine.

A governed run distinguishes *what went wrong* with exactly three
outcomes:

- ``REVISE``    — the draft is wrong; regenerate the output.
- ``REPAIR``    — the evidence is wrong; return to retrieval.
- ``STARTOVER`` — the premise is wrong; **human-only**, never
  agent-initiated.

The human-only rule for ``STARTOVER`` is enforced structurally: the
transition requires a :class:`HumanWarrant`, and constructing a warrant
requires a named human approver. An agent passing
``initiated_by=Initiator.AGENT`` — or omitting the warrant — raises
:class:`StartoverNotPermittedError` regardless of any other argument.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable, Dict, FrozenSet, List, Optional, Tuple


class Outcome(Enum):
    """The three failure outcomes. There is deliberately no fourth."""

    REVISE = "revise"
    REPAIR = "repair"
    STARTOVER = "startover"


class Initiator(Enum):
    AGENT = "agent"
    HUMAN = "human"


class RunState(Enum):
    RETRIEVING = "retrieving"
    DRAFTING = "drafting"
    CHECKING = "checking"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    STARTED_OVER = "started_over"


@dataclass(frozen=True)
class HumanWarrant:
    """Proof that a named human authorized a startover.

    The warrant is the *only* path to a ``STARTOVER`` transition. It is
    deliberately impossible to construct without naming an approver.
    """

    approver: str
    reason: str

    def __post_init__(self) -> None:
        if not self.approver.strip():
            raise ValueError("a HumanWarrant requires a named approver")
        if not self.reason.strip():
            raise ValueError("a HumanWarrant requires a reason")


class StartoverNotPermittedError(PermissionError):
    """Raised when anything other than a warranted human initiates startover."""


class InvalidTransitionError(RuntimeError):
    """Raised on a transition the state machine does not allow."""


@dataclass(frozen=True)
class Transition:
    at: str
    from_state: RunState
    to_state: RunState
    outcome: Optional[Outcome]
    initiated_by: Initiator
    reason: str


# Forward-progress transitions (state -> allowed next states).
_PROGRESS: Dict[RunState, FrozenSet[RunState]] = {
    RunState.RETRIEVING: frozenset({RunState.DRAFTING}),
    RunState.DRAFTING: frozenset({RunState.CHECKING}),
    RunState.CHECKING: frozenset({RunState.AWAITING_APPROVAL}),
    RunState.AWAITING_APPROVAL: frozenset({RunState.APPROVED}),
    RunState.APPROVED: frozenset(),
    RunState.STARTED_OVER: frozenset({RunState.RETRIEVING}),
}

# Failure outcomes are only decidable from the CHECKING state (that is
# where scrubber/sentinel verdicts land), and each maps to exactly one
# destination.
_FAILURE_TARGET: Dict[Outcome, RunState] = {
    Outcome.REVISE: RunState.DRAFTING,
    Outcome.REPAIR: RunState.RETRIEVING,
    Outcome.STARTOVER: RunState.STARTED_OVER,
}

AuditHook = Callable[[str, Dict[str, str]], None]


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class GovernanceStateMachine:
    """Tracks a governed run through retrieval, drafting, checks, and approval.

    An optional ``audit_hook`` receives ``(action, detail)`` for every
    transition, so the machine can write to an
    :class:`~agent_governance_kit.audit.AuditLog` without depending on it.
    """

    def __init__(
        self,
        initial: RunState = RunState.RETRIEVING,
        audit_hook: Optional[AuditHook] = None,
    ) -> None:
        self._state = initial
        self._history: List[Transition] = []
        self._audit_hook = audit_hook

    @property
    def state(self) -> RunState:
        return self._state

    @property
    def history(self) -> Tuple[Transition, ...]:
        return tuple(self._history)

    def _record(
        self,
        to_state: RunState,
        outcome: Optional[Outcome],
        initiated_by: Initiator,
        reason: str,
    ) -> Transition:
        transition = Transition(
            at=_utcnow(),
            from_state=self._state,
            to_state=to_state,
            outcome=outcome,
            initiated_by=initiated_by,
            reason=reason,
        )
        self._state = to_state
        self._history.append(transition)
        if self._audit_hook is not None:
            self._audit_hook(
                "state_transition",
                {
                    "from": transition.from_state.value,
                    "to": transition.to_state.value,
                    "outcome": outcome.value if outcome else "",
                    "initiated_by": initiated_by.value,
                    "reason": reason,
                },
            )
        return transition

    def advance(self, to_state: RunState, reason: str = "") -> Transition:
        """Move forward along the normal (non-failure) path."""
        if to_state not in _PROGRESS[self._state]:
            raise InvalidTransitionError(
                f"cannot advance from {self._state.value} to {to_state.value}"
            )
        return self._record(to_state, None, Initiator.AGENT, reason)

    def fail(
        self,
        outcome: Outcome,
        reason: str,
        initiated_by: Initiator = Initiator.AGENT,
        warrant: Optional[HumanWarrant] = None,
    ) -> Transition:
        """Apply a failure outcome from the CHECKING state.

        ``STARTOVER`` requires ``initiated_by=Initiator.HUMAN`` **and** a
        :class:`HumanWarrant`; every other combination raises
        :class:`StartoverNotPermittedError`. ``REVISE`` and ``REPAIR``
        are agent-decidable.
        """
        if self._state is not RunState.CHECKING:
            raise InvalidTransitionError(
                f"failure outcomes are only decidable from checking; "
                f"current state is {self._state.value}"
            )
        if outcome is Outcome.STARTOVER:
            if initiated_by is not Initiator.HUMAN:
                raise StartoverNotPermittedError(
                    "startover is human-only: an agent attempted to trigger it"
                )
            if warrant is None:
                raise StartoverNotPermittedError(
                    "startover requires a HumanWarrant naming the approver"
                )
            reason = f"{reason} [warrant: {warrant.approver}: {warrant.reason}]"
        return self._record(_FAILURE_TARGET[outcome], outcome, initiated_by, reason)
