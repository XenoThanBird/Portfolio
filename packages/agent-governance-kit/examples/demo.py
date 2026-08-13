"""End-to-end demo of the Agent Governance Kit.

Runs a complete governed cycle in a few milliseconds, using synthetic
data only:

1. draft with sensitive strings + a policy violation
2. scrubber redacts, sentinel fails the draft  ->  REVISE (agent-decidable)
3. an agent tries STARTOVER and is refused (human-only, audited)
4. revised draft passes checks  ->  HITL gate blocks for approval
5. a second gate instance (the "reviewer process") approves
6. the audit chain verifies end-to-end; then we tamper with a copy and
   watch verification catch it at the exact record

Run:  python examples/demo.py
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from agent_governance_kit import (  # noqa: E402
    AuditLog,
    ForbiddenTermsPolicy,
    GovernanceStateMachine,
    HITLGate,
    HumanWarrant,
    Initiator,
    MaxLengthPolicy,
    Outcome,
    RequiredFieldsPolicy,
    RunState,
    Scrubber,
    Sentinel,
    StartoverNotPermittedError,
)


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="agk_demo_"))
    audit = AuditLog(workdir / "audit.jsonl")
    gate_store = workdir / "approvals"
    requester = HITLGate(gate_store)
    machine = GovernanceStateMachine(
        audit_hook=lambda action, detail: audit.append("state_machine", action, dict(detail)),
        warrant_verifier=requester.startover_verifier(),
    )
    scrubber = Scrubber()
    sentinel = Sentinel(
        [
            RequiredFieldsPolicy(["title", "body"]),
            MaxLengthPolicy("body", 200),
            ForbiddenTermsPolicy("body", ["guaranteed returns"]),
        ]
    )

    print("=== Agent Governance Kit — end-to-end demo (synthetic data) ===\n")

    # 1. Retrieval -> first draft, containing PII and a forbidden claim.
    machine.advance(RunState.DRAFTING, reason="evidence retrieved")
    draft = {
        "title": "Investment brief",
        "body": (
            "Contact jane.doe@example.test or 555-867-5309. "
            "This product offers guaranteed returns."
        ),
    }
    audit.append("agent", "draft_created", {"chars": len(draft["body"])})
    machine.advance(RunState.CHECKING, reason="draft ready")

    # 2. Check stage: scrub, then evaluate policies.
    scrubbed = scrubber.scrub(draft["body"])
    audit.append("scrubber", "redactions_applied", dict(scrubbed.redactions))
    print(f"[scrubber] redacted: {scrubbed.redactions}")
    checked = sentinel.check({**draft, "body": scrubbed.text})
    print(f"[sentinel] passed={checked.passed} reasons={checked.reasons()}")
    audit.append("sentinel", "policy_check", {"passed": checked.passed, "failures": checked.reasons()})

    # The draft is wrong (forbidden claim) -> agent decides REVISE.
    machine.fail(Outcome.REVISE, reason="; ".join(checked.reasons()))
    print(f"[machine]  outcome=revise -> state={machine.state.value}")

    # 3. A frustrated agent tries to start over. Refused: human-only.
    machine.advance(RunState.CHECKING, reason="revised draft ready")
    try:
        machine.fail(Outcome.STARTOVER, reason="agent gives up", initiated_by=Initiator.AGENT)
    except StartoverNotPermittedError as exc:
        # The machine already audited the denial through its hook.
        print(f"[machine]  agent startover DENIED: {exc}")

    # 3b. The agent escalates: it forges a warrant and *claims* to be
    #     human. The approval boundary finds no backing record.
    forged = HumanWarrant(approver="mallory", reason="trust me", approval_id="deadbeef")
    try:
        machine.fail(
            Outcome.STARTOVER,
            reason="forged claim",
            initiated_by=Initiator.HUMAN,
            warrant=forged,
        )
    except StartoverNotPermittedError as exc:
        print(f"[machine]  forged warrant DENIED: {exc}")

    # 4. Revised draft: clean, compliant.
    draft["body"] = "Projected performance varies; see the attached risk disclosure."
    scrubbed = scrubber.scrub(draft["body"])
    checked = sentinel.check({**draft, "body": scrubbed.text})
    audit.append("sentinel", "policy_check", {"passed": checked.passed, "failures": checked.reasons()})
    print(f"[sentinel] passed={checked.passed} (revised draft)")
    machine.advance(RunState.AWAITING_APPROVAL, reason="all checks green")

    # 5. HITL gate: requester blocks; a second instance (the reviewer
    #    "process") loads the same store and approves.
    approval = requester.request("publish investment brief", {"title": draft["title"]})
    audit.append("hitl", "approval_requested", {"approval_id": approval.id})
    HITLGate(gate_store).approve(approval.id, decided_by="demo-reviewer", note="clean + compliant")
    decided = requester.wait(approval.id, timeout=10)
    print(f"[hitl]     {decided.status.value} by {decided.decided_by}: {decided.note}")
    audit.append("hitl", "approval_decided", {"approval_id": approval.id, "status": decided.status.value})
    machine.advance(RunState.APPROVED, reason=f"approved by {decided.decided_by}")

    # 6. Verify the chain; then tamper with a copy and catch it.
    result = audit.verify()
    print(f"\n[audit]    chain valid={result.valid} across {result.records_checked} records")

    tampered_path = workdir / "tampered.jsonl"
    shutil.copy(audit.path, tampered_path)
    lines = tampered_path.read_text(encoding="utf-8").strip().splitlines()
    target = next(i for i, line in enumerate(lines) if "draft_created" in line)
    lines[target] = lines[target].replace("draft_created", "nothing_to_see")
    tampered_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    verdict = AuditLog.verify_file(tampered_path)
    print(
        f"[audit]    tampered copy: valid={verdict.valid}, "
        f"first broken link = record {verdict.first_broken_index} ({verdict.reason})"
    )

    ok = (
        machine.state is RunState.APPROVED
        and result.valid
        and not verdict.valid
        and verdict.first_broken_index == target
    )
    print(f"\n=== demo {'PASSED' if ok else 'FAILED'} — run state: {machine.state.value} ===")
    shutil.rmtree(workdir, ignore_errors=True)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
