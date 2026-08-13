"""Failure semantics as a first-class state machine.

A governed run distinguishes *what went wrong* with exactly three
outcomes:

- ``REVISE``    — the draft is wrong; regenerate the output.
- ``REPAIR``    — the evidence is wrong; return to retrieval.
- ``STARTOVER`` — the premise is wrong; **human-only**, never
  agent-initiated.

The human-only rule for ``STARTOVER`` is enforced against a trusted
approval boundary, not caller assertion: the machine must be
constructed with a ``warrant_verifier`` (normally
:meth:`agent_governance_kit.hitl.HITLGate.startover_verifier`, which
validates the warrant against a persisted, human-decided approval
record). Without a verifier, startover is denied entirely — secure by
default. A warrant that the verifier rejects, an agent initiator, a
missing warrant, or a replayed warrant all raise
:class:`StartoverNotPermittedError` and leave the state untouched.

In-process Python cannot provide true capability security — a caller
with arbitrary code execution can forge any object. The trust boundary
is therefore the approval *store* (protect it with OS-level
permissions so agents cannot write it); the kit's job is to make the
legitimate path verifiable and every illegitimate path a loud,
auditable refusal. See ARCHITECTURE.md for the full trust model.
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
    """A claim that a named human authorized a startover.

    A warrant is *not* proof by itself — it must reference an approval
    (``approval_id``) that the machine's ``warrant_verifier`` can check
    against a trusted approval boundary such as the HITL gate's store.
    """

    approver: str
    reason: str
    approval_id: str

    def __post_init__(self) -> None:
        if not self.approver.strip():
            raise ValueError("a HumanWarrant requires a named approver")
        if not self.reason.strip():
            raise ValueError("a HumanWarrant requires a reason")
        if not self.approval_id.strip():
            raise ValueError("a HumanWarrant requires the approval id it is based on")


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

# Returns None when the warrant is genuine, or a human-readable reason
# for rejection. Normally HITLGate.startover_verifier().
WarrantVerifier = Callable[[HumanWarrant], Optional[str]]


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
        warrant_verifier: Optional[WarrantVerifier] = None,
    ) -> None:
        self._state = initial
        self._history: List[Transition] = []
        self._audit_hook = audit_hook
        self._warrant_verifier = warrant_verifier
        self._used_warrants: set[str] = set()

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

        ``REVISE`` and ``REPAIR`` are agent-decidable. ``STARTOVER``
        requires ``initiated_by=Initiator.HUMAN``, a
        :class:`HumanWarrant`, **and** a configured ``warrant_verifier``
        that accepts the warrant against the trusted approval boundary.
        A warrant is single-use. Every other combination raises
        :class:`StartoverNotPermittedError` without touching the state.
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
            if self._warrant_verifier is None:
                raise StartoverNotPermittedError(
                    "startover is disabled: no trusted approval boundary "
                    "(warrant_verifier) is configured on this machine"
                )
            if warrant.approval_id in self._used_warrants:
                raise StartoverNotPermittedError(
                    f"warrant for approval {warrant.approval_id} was already used"
                )
            rejection = self._warrant_verifier(warrant)
            if rejection is not None:
                raise StartoverNotPermittedError(
                    f"warrant rejected by approval boundary: {rejection}"
                )
            self._used_warrants.add(warrant.approval_id)
            reason = (
                f"{reason} [warrant: {warrant.approver}: {warrant.reason} "
                f"(approval {warrant.approval_id})]"
            )
        return self._record(_FAILURE_TARGET[outcome], outcome, initiated_by, reason)
