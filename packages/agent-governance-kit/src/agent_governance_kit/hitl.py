"""Human-in-the-loop gate: a blocking approval checkpoint with
serializable pending state.

Each approval request is persisted as one JSON file in the gate's store
directory, so a run can stop at the gate, the process can exit, and a
different process (a reviewer CLI, a web approval surface, an operator
console) can load the same store, decide, and let the original run — or
a resumed one — proceed.

State transitions are one-way: PENDING → APPROVED | REJECTED. Deciding
an already-decided request raises :class:`AlreadyDecidedError`.
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .outcomes import HumanWarrant

STARTOVER_SCOPE = "startover"


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Approval:
    """The serializable state of one approval request."""

    id: str
    subject: str
    payload: Dict[str, Any]
    status: ApprovalStatus
    requested_at: str
    requested_by: str
    decided_at: Optional[str] = None
    decided_by: Optional[str] = None
    note: Optional[str] = None

    def to_json(self) -> str:
        d = asdict(self)
        d["status"] = self.status.value
        return json.dumps(d, sort_keys=True, indent=2)

    @classmethod
    def from_json(cls, raw: str) -> "Approval":
        d = json.loads(raw)
        d["status"] = ApprovalStatus(d["status"])
        return cls(**d)


class UnknownApprovalError(KeyError):
    """Raised when an approval id has no state in the store."""


class AlreadyDecidedError(RuntimeError):
    """Raised when deciding a request that is no longer pending."""


class ApprovalTimeoutError(TimeoutError):
    """Raised when a blocking wait exceeds its deadline."""


class HITLGate:
    """File-backed approval gate, resumable across processes."""

    def __init__(self, store: Union[str, Path]) -> None:
        self.store = Path(store)
        self.store.mkdir(parents=True, exist_ok=True)

    def _path(self, approval_id: str) -> Path:
        return self.store / f"{approval_id}.json"

    def _load(self, approval_id: str) -> Approval:
        path = self._path(approval_id)
        if not path.exists():
            raise UnknownApprovalError(approval_id)
        return Approval.from_json(path.read_text(encoding="utf-8"))

    def _save(self, approval: Approval) -> None:
        self._path(approval.id).write_text(approval.to_json(), encoding="utf-8")

    def request(
        self,
        subject: str,
        payload: Optional[Dict[str, Any]] = None,
        requested_by: str = "agent",
    ) -> Approval:
        """Create a PENDING approval and persist it."""
        approval = Approval(
            id=uuid.uuid4().hex,
            subject=subject,
            payload=payload or {},
            status=ApprovalStatus.PENDING,
            requested_at=datetime.now(timezone.utc).isoformat(),
            requested_by=requested_by,
        )
        self._save(approval)
        return approval

    def status(self, approval_id: str) -> Approval:
        return self._load(approval_id)

    def pending(self) -> List[Approval]:
        """All PENDING requests in the store (any process's)."""
        out = []
        for path in sorted(self.store.glob("*.json")):
            approval = Approval.from_json(path.read_text(encoding="utf-8"))
            if approval.status is ApprovalStatus.PENDING:
                out.append(approval)
        return out

    def _decide(self, approval_id: str, status: ApprovalStatus, decided_by: str, note: str) -> Approval:
        current = self._load(approval_id)
        if current.status is not ApprovalStatus.PENDING:
            raise AlreadyDecidedError(
                f"approval {approval_id} is already {current.status.value}"
            )
        decided = Approval(
            **{
                **asdict(current),
                "status": status,
                "decided_at": datetime.now(timezone.utc).isoformat(),
                "decided_by": decided_by,
                "note": note,
            }
        )
        self._save(decided)
        return decided

    def approve(self, approval_id: str, decided_by: str, note: str = "") -> Approval:
        return self._decide(approval_id, ApprovalStatus.APPROVED, decided_by, note)

    def reject(self, approval_id: str, decided_by: str, note: str = "") -> Approval:
        return self._decide(approval_id, ApprovalStatus.REJECTED, decided_by, note)

    def request_startover(
        self,
        subject: str,
        payload: Optional[Dict[str, Any]] = None,
        requested_by: str = "agent",
    ) -> Approval:
        """Create a PENDING approval explicitly scoped to startover.

        Only approvals created with this scope can back a
        :class:`~agent_governance_kit.outcomes.HumanWarrant` — an
        unrelated approved request cannot be replayed as a startover
        authorization.
        """
        scoped = dict(payload or {})
        scoped["scope"] = STARTOVER_SCOPE
        return self.request(subject, scoped, requested_by)

    def startover_verifier(self) -> Callable[[HumanWarrant], Optional[str]]:
        """A warrant verifier bound to this gate's store.

        Wire it into ``GovernanceStateMachine(warrant_verifier=...)``.
        The warrant is genuine only if its ``approval_id`` names a
        startover-scoped approval in this store that a human APPROVED,
        and the warrant's approver matches the recorded decider.
        """

        def verify(warrant: HumanWarrant) -> Optional[str]:
            try:
                approval = self._load(warrant.approval_id)
            except UnknownApprovalError:
                return f"no approval {warrant.approval_id} exists in the store"
            if approval.payload.get("scope") != STARTOVER_SCOPE:
                return "approval is not scoped to startover"
            if approval.status is not ApprovalStatus.APPROVED:
                return f"approval is {approval.status.value}, not approved"
            if approval.decided_by != warrant.approver:
                return (
                    f"warrant approver {warrant.approver!r} does not match "
                    f"recorded decider {approval.decided_by!r}"
                )
            return None

        return verify

    def wait(
        self,
        approval_id: str,
        timeout: float = 300.0,
        poll_interval: float = 0.2,
    ) -> Approval:
        """Block until the request is decided; raise on timeout.

        Because state lives in the store, the deciding process does not
        need to be the waiting process.
        """
        deadline = time.monotonic() + timeout
        while True:
            approval = self._load(approval_id)
            if approval.status is not ApprovalStatus.PENDING:
                return approval
            if time.monotonic() >= deadline:
                raise ApprovalTimeoutError(
                    f"approval {approval_id} still pending after {timeout}s"
                )
            time.sleep(poll_interval)
