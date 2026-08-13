"""Scrubber: redaction and sensitive-content filtering with pluggable rules.

A :class:`RedactionRule` is a named regex + replacement token. The
scrubber applies every rule and reports which rules fired and how many
times — the *fact* of redaction is auditable without the audit trail
ever containing the sensitive value itself.

The default ruleset covers common synthetic-fixture shapes (emails,
North-American phone numbers, SSN-shaped strings, API-key-shaped
strings). It is a starting point, not a compliance guarantee: real
deployments should extend it to their own data classes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Pattern, Sequence


@dataclass(frozen=True)
class RedactionRule:
    """One named redaction pattern."""

    name: str
    pattern: Pattern[str]
    replacement: str

    @classmethod
    def from_regex(cls, name: str, regex: str, replacement: str) -> "RedactionRule":
        return cls(name=name, pattern=re.compile(regex), replacement=replacement)


@dataclass(frozen=True)
class ScrubResult:
    """Scrubbed text plus a per-rule count of redactions applied."""

    text: str
    redactions: Dict[str, int] = field(default_factory=dict)

    @property
    def clean(self) -> bool:
        return not self.redactions

    @property
    def total_redactions(self) -> int:
        return sum(self.redactions.values())


def default_rules() -> List[RedactionRule]:
    """Baseline rules for common sensitive-string shapes (synthetic-safe)."""
    return [
        RedactionRule.from_regex(
            "email",
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            "[REDACTED:email]",
        ),
        RedactionRule.from_regex(
            "phone",
            r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "[REDACTED:phone]",
        ),
        RedactionRule.from_regex(
            "ssn",
            r"\b\d{3}-\d{2}-\d{4}\b",
            "[REDACTED:ssn]",
        ),
        RedactionRule.from_regex(
            "api_key",
            r"\b(?:sk|pk|api|key)[-_][A-Za-z0-9_-]{16,}\b",
            "[REDACTED:api_key]",
        ),
    ]


class Scrubber:
    """Applies an ordered, pluggable set of redaction rules."""

    def __init__(self, rules: Sequence[RedactionRule] = ()) -> None:
        self._rules: List[RedactionRule] = list(rules) if rules else default_rules()

    @property
    def rules(self) -> Sequence[RedactionRule]:
        return tuple(self._rules)

    def add_rule(self, rule: RedactionRule) -> None:
        self._rules.append(rule)

    def scrub(self, text: str) -> ScrubResult:
        redactions: Dict[str, int] = {}
        for rule in self._rules:
            text, count = rule.pattern.subn(rule.replacement, text)
            if count:
                redactions[rule.name] = redactions.get(rule.name, 0) + count
        return ScrubResult(text=text, redactions=redactions)
