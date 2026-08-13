"""Scrubber tests — synthetic fixtures only."""

from __future__ import annotations

from agent_governance_kit import RedactionRule, Scrubber


class TestDefaultRules:
    def test_email_redacted(self) -> None:
        result = Scrubber().scrub("contact jane.doe@example.test for details")
        assert "jane.doe@example.test" not in result.text
        assert "[REDACTED:email]" in result.text
        assert result.redactions == {"email": 1}

    def test_phone_redacted(self) -> None:
        result = Scrubber().scrub("call 555-867-5309 today")
        assert "[REDACTED:phone]" in result.text

    def test_ssn_shaped_redacted(self) -> None:
        result = Scrubber().scrub("id 078-05-1120 on file")
        assert "[REDACTED:ssn]" in result.text

    def test_api_key_shaped_redacted(self) -> None:
        result = Scrubber().scrub("token sk-abcdefghijklmnop1234 leaked")
        assert "[REDACTED:api_key]" in result.text

    def test_clean_text_untouched(self) -> None:
        text = "the quarterly summary is ready for review"
        result = Scrubber().scrub(text)
        assert result.text == text
        assert result.clean
        assert result.total_redactions == 0

    def test_multiple_hits_counted(self) -> None:
        result = Scrubber().scrub("a@example.test and b@example.test")
        assert result.redactions == {"email": 2}
        assert result.total_redactions == 2


class TestPluggableRules:
    def test_custom_rule_set_replaces_defaults(self) -> None:
        rule = RedactionRule.from_regex("badge", r"BADGE-\d{4}", "[REDACTED:badge]")
        scrubber = Scrubber(rules=[rule])
        result = scrubber.scrub("employee BADGE-1234 with a@example.test")
        assert "[REDACTED:badge]" in result.text
        assert "a@example.test" in result.text  # defaults not active

    def test_add_rule_extends(self) -> None:
        scrubber = Scrubber()
        scrubber.add_rule(
            RedactionRule.from_regex("ticket", r"TKT-\d{6}", "[REDACTED:ticket]")
        )
        result = scrubber.scrub("see TKT-000042 filed by a@example.test")
        assert "[REDACTED:ticket]" in result.text
        assert "[REDACTED:email]" in result.text
