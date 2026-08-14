# Agent Governance Kit

Governance primitives for agentic AI systems — the controls an agent
pipeline needs before anyone should trust its output: a tamper-evident
audit trail, a redaction/policy check stage, failure semantics that
distinguish *what went wrong*, and a human approval gate that survives
process restarts.

**Framework-agnostic by construction: zero runtime dependencies.**
Adapters for specific orchestration frameworks can be added as optional
extras; the core never imports one.

## The five primitives

| Primitive | What it guarantees |
| ---- | ---- |
| `AuditLog` | Append-only JSONL, SHA-256 hash-chained. `verify()` detects any mutation, insertion, or deletion and names the first broken record. |
| `Scrubber` | Pluggable redaction rules; reports *which* rules fired and how often, so redaction is auditable without logging the sensitive value. |
| `Sentinel` | Policy-as-code: every policy returns pass/fail **with a reason**; all violations surface, not just the first. |
| `GovernanceStateMachine` | Exactly three failure outcomes — `revise` (draft wrong), `repair` (evidence wrong), `startover` (premise wrong). Startover is **human-only**, verified against the HITL gate's persisted approval records (a `HumanWarrant` must reference a human-APPROVED, startover-scoped approval; warrants are single-use; no verifier configured → startover disabled). Agent-initiated and forged attempts raise, auditable. |
| `HITLGate` | Blocking approval checkpoint. Pending state is one JSON file per request, so a different process can load the store, decide, and unblock the run. |

## Quickstart (< 60 seconds)

```bash
cd packages/agent-governance-kit
make demo          # or: python examples/demo.py
```

The demo runs a full governed cycle on synthetic data: a draft with
sensitive strings and a policy violation is scrubbed, fails the
sentinel, is revised (agent-decidable), an agent's startover attempt is
refused and audited, the clean revision passes, a simulated reviewer
process approves it at the gate — and then the audit chain is verified,
tampered with, and the tampering is caught at the exact record.

## Usage sketch

```python
from agent_governance_kit import (
    AuditLog, Scrubber, Sentinel, ForbiddenTermsPolicy,
    GovernanceStateMachine, RunState, Outcome, HITLGate,
)

audit = AuditLog("run/audit.jsonl")
machine = GovernanceStateMachine(
    audit_hook=lambda action, d: audit.append("state_machine", action, dict(d))
)
scrubber = Scrubber()                       # default rules; pluggable
sentinel = Sentinel([ForbiddenTermsPolicy("body", ["guaranteed returns"])])

machine.advance(RunState.DRAFTING)
machine.advance(RunState.CHECKING)
clean = scrubber.scrub(draft_text)
verdicts = sentinel.check({"body": clean.text})
if not verdicts.passed:
    machine.fail(Outcome.REVISE, reason="; ".join(verdicts.reasons()))

# later, once checks pass:
gate = HITLGate("run/approvals")
req = gate.request("publish draft", {"run": "r-1"})
decision = gate.wait(req.id, timeout=3600)   # another process approves
assert audit.verify().valid
```

## Development

```bash
pip install -e .[dev]
make test          # pytest with coverage (audit + state machine ≥ 80% required)
make typecheck     # mypy --strict
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the design, the trust model,
and what the hash chain does and does not protect against.

All fixtures and examples are synthetic. License: Apache-2.0
(see repository root).
