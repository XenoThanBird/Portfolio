"""Sentinel policy-as-code tests."""

from __future__ import annotations

from typing import Any, Dict

from agent_governance_kit import (
    ForbiddenTermsPolicy,
    MaxLengthPolicy,
    PolicyVerdict,
    RequiredFieldsPolicy,
    Sentinel,
)


def make_sentinel() -> Sentinel:
    return Sentinel(
        [
            RequiredFieldsPolicy(["title", "body"]),
            MaxLengthPolicy("body", 100),
            ForbiddenTermsPolicy("body", ["guaranteed returns", "risk-free"]),
        ]
    )


class TestVerdicts:
    def test_compliant_payload_passes_all(self) -> None:
        result = make_sentinel().check({"title": "Q3 summary", "body": "totals attached"})
        assert result.passed
        assert len(result.verdicts) == 3
        assert not result.failures

    def test_all_violations_surface_not_just_first(self) -> None:
        result = make_sentinel().check({"body": "risk-free " + "x" * 200})
        assert not result.passed
        assert len(result.failures) == 3  # missing title, too long, forbidden term
        reasons = " | ".join(result.reasons())
        assert "missing" in reasons and "exceeds" in reasons and "forbidden" in reasons

    def test_forbidden_terms_case_insensitive(self) -> None:
        policy = ForbiddenTermsPolicy("body", ["Insider"])
        verdict = policy.evaluate({"body": "based on INSIDER information"})
        assert not verdict.passed

    def test_every_verdict_carries_a_reason(self) -> None:
        result = make_sentinel().check({"title": "t", "body": "fine"})
        assert all(v.reason for v in result.verdicts)


class TestPluggability:
    def test_custom_policy_via_protocol(self) -> None:
        class EvenWordCountPolicy:
            @property
            def name(self) -> str:
                return "even_word_count"

            def evaluate(self, payload: Dict[str, Any]) -> PolicyVerdict:
                count = len(str(payload.get("body", "")).split())
                return PolicyVerdict(
                    self.name, count % 2 == 0, f"{count} words"
                )

        sentinel = Sentinel()
        sentinel.register(EvenWordCountPolicy())
        assert sentinel.check({"body": "two words"}).passed
        assert not sentinel.check({"body": "three little words"}).passed

    def test_empty_sentinel_passes(self) -> None:
        assert Sentinel().check({"anything": True}).passed
