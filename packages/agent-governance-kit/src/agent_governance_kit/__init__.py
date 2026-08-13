"""Agent Governance Kit — governance primitives for agentic AI systems.

Framework-agnostic (zero runtime dependencies). Five primitives:

- :class:`AuditLog` — append-only, hash-chained audit trail with
  tamper detection (:meth:`AuditLog.verify`).
- :class:`Scrubber` — redaction / sensitive-content filtering with a
  pluggable rule set.
- :class:`Sentinel` — policy-as-code evaluation returning pass/fail
  with reasons.
- :class:`GovernanceStateMachine` — failure semantics with exactly
  three outcomes (revise / repair / startover), startover human-only.
- :class:`HITLGate` — blocking human approval checkpoint with
  serializable, cross-process-resumable pending state.
"""

from .audit import (
    AuditIntegrityError,
    AuditLog,
    AuditRecord,
    GENESIS_HASH,
    VerificationResult,
)
from .hitl import (
    STARTOVER_SCOPE,
    AlreadyDecidedError,
    Approval,
    ApprovalStatus,
    ApprovalTimeoutError,
    HITLGate,
    UnknownApprovalError,
)
from .outcomes import (
    GovernanceStateMachine,
    HumanWarrant,
    Initiator,
    InvalidTransitionError,
    Outcome,
    RunState,
    StartoverNotPermittedError,
    Transition,
    WarrantVerifier,
)
from .scrubber import RedactionRule, ScrubResult, Scrubber, default_rules
from .sentinel import (
    ForbiddenTermsPolicy,
    MaxLengthPolicy,
    Policy,
    PolicyVerdict,
    RequiredFieldsPolicy,
    Sentinel,
    SentinelResult,
)

__version__ = "0.1.0"

__all__ = [
    "GENESIS_HASH",
    "STARTOVER_SCOPE",
    "AlreadyDecidedError",
    "Approval",
    "ApprovalStatus",
    "ApprovalTimeoutError",
    "AuditIntegrityError",
    "AuditLog",
    "AuditRecord",
    "ForbiddenTermsPolicy",
    "GovernanceStateMachine",
    "HITLGate",
    "HumanWarrant",
    "Initiator",
    "InvalidTransitionError",
    "MaxLengthPolicy",
    "Outcome",
    "Policy",
    "PolicyVerdict",
    "RedactionRule",
    "RequiredFieldsPolicy",
    "RunState",
    "ScrubResult",
    "Scrubber",
    "Sentinel",
    "SentinelResult",
    "StartoverNotPermittedError",
    "Transition",
    "UnknownApprovalError",
    "VerificationResult",
    "WarrantVerifier",
    "default_rules",
]
