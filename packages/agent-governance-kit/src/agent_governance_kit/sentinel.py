"""Sentinel: policy-as-code evaluation returning pass/fail with reasons.

A policy is any object satisfying the :class:`Policy` protocol — a name
plus an ``evaluate`` returning a :class:`PolicyVerdict`. The sentinel
runs every policy (no short-circuiting: a failed check should surface
*all* violations, not just the first) and aggregates the verdicts.

Three reference policies ship with the kit; real deployments register
their own.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, Sequence, Tuple, runtime_checkable


@dataclass(frozen=True)
class PolicyVerdict:
    policy: str
    passed: bool
    reason: str


@runtime_checkable
class Policy(Protocol):
    """Anything with a name and an evaluate() is a policy."""

    @property
    def name(self) -> str: ...

    def evaluate(self, payload: Dict[str, Any]) -> PolicyVerdict: ...


@dataclass(frozen=True)
class SentinelResult:
    passed: bool
    verdicts: Tuple[PolicyVerdict, ...]

    @property
    def failures(self) -> Tuple[PolicyVerdict, ...]:
        return tuple(v for v in self.verdicts if not v.passed)

    def reasons(self) -> List[str]:
        return [f"{v.policy}: {v.reason}" for v in self.failures]


class Sentinel:
    """Evaluates a payload against every registered policy."""

    def __init__(self, policies: Sequence[Policy] = ()) -> None:
        self._policies: List[Policy] = list(policies)

    @property
    def policies(self) -> Sequence[Policy]:
        return tuple(self._policies)

    def register(self, policy: Policy) -> None:
        self._policies.append(policy)

    def check(self, payload: Dict[str, Any]) -> SentinelResult:
        verdicts = tuple(policy.evaluate(payload) for policy in self._policies)
        return SentinelResult(
            passed=all(v.passed for v in verdicts),
            verdicts=verdicts,
        )


# ── Reference policies ────────────────────────────────────────────────


class MaxLengthPolicy:
    """Fail drafts longer than a character budget."""

    def __init__(self, field: str, max_chars: int) -> None:
        self._field = field
        self._max = max_chars

    @property
    def name(self) -> str:
        return f"max_length[{self._field}<={self._max}]"

    def evaluate(self, payload: Dict[str, Any]) -> PolicyVerdict:
        value = str(payload.get(self._field, ""))
        if len(value) > self._max:
            return PolicyVerdict(self.name, False, f"{len(value)} chars exceeds {self._max}")
        return PolicyVerdict(self.name, True, "within budget")


class ForbiddenTermsPolicy:
    """Fail drafts containing any forbidden term (case-insensitive)."""

    def __init__(self, field: str, terms: Sequence[str]) -> None:
        self._field = field
        self._terms = tuple(t.lower() for t in terms)

    @property
    def name(self) -> str:
        return f"forbidden_terms[{self._field}]"

    def evaluate(self, payload: Dict[str, Any]) -> PolicyVerdict:
        value = str(payload.get(self._field, "")).lower()
        hits = [t for t in self._terms if t in value]
        if hits:
            return PolicyVerdict(self.name, False, f"contains forbidden terms: {', '.join(hits)}")
        return PolicyVerdict(self.name, True, "no forbidden terms")


class RequiredFieldsPolicy:
    """Fail payloads missing required keys (or with empty values)."""

    def __init__(self, fields: Sequence[str]) -> None:
        self._fields = tuple(fields)

    @property
    def name(self) -> str:
        return f"required_fields[{','.join(self._fields)}]"

    def evaluate(self, payload: Dict[str, Any]) -> PolicyVerdict:
        missing = [f for f in self._fields if not payload.get(f)]
        if missing:
            return PolicyVerdict(self.name, False, f"missing or empty: {', '.join(missing)}")
        return PolicyVerdict(self.name, True, "all required fields present")
