"""Evidence core tests: the no-unclassified-figures rule and the
provenance-inheritance aggregation rules."""

from __future__ import annotations

import pytest

from value_registry import (
    EvidenceClass,
    Figure,
    UnclassifiedFigureError,
    derived,
    parse_figure,
    weakest,
    weighted_aggregate,
)


class TestFigure:
    def test_confidence_bounds_enforced(self) -> None:
        with pytest.raises(ValueError):
            Figure(1.0, EvidenceClass.DOCUMENTED, 1.2)
        with pytest.raises(ValueError):
            Figure(1.0, EvidenceClass.DOCUMENTED, -0.1)

    def test_render_shows_class_and_confidence(self) -> None:
        fig = Figure(250000, EvidenceClass.MODELED, 0.5, unit="USD")
        rendered = fig.render(",.0f")
        assert rendered == "250,000 USD [modeled, conf 0.50]"

    def test_to_dict_roundtrip(self) -> None:
        fig = Figure(3.5, EvidenceClass.ESTIMATED, 0.7, source="workshop")
        assert parse_figure(fig.to_dict(), "roundtrip") == fig


class TestRefusal:
    """The engine refuses to ingest an unclassified figure."""

    def test_bare_number_refused(self) -> None:
        with pytest.raises(UnclassifiedFigureError, match="bare number"):
            parse_figure(42, "scores.financial_impact")

    def test_bare_float_refused(self) -> None:
        with pytest.raises(UnclassifiedFigureError, match="bare number"):
            parse_figure(3.14, "x")

    def test_missing_evidence_refused(self) -> None:
        with pytest.raises(UnclassifiedFigureError, match="missing evidence"):
            parse_figure({"value": 4, "confidence": 0.5}, "x")

    def test_missing_confidence_refused(self) -> None:
        with pytest.raises(UnclassifiedFigureError, match="missing confidence"):
            parse_figure({"value": 4, "evidence": "estimated"}, "x")

    def test_unknown_class_refused(self) -> None:
        with pytest.raises(UnclassifiedFigureError, match="unknown evidence class"):
            parse_figure({"value": 4, "evidence": "vibes", "confidence": 0.9}, "x")

    def test_non_numeric_value_refused(self) -> None:
        with pytest.raises(UnclassifiedFigureError, match="numeric"):
            parse_figure({"value": "big", "evidence": "modeled", "confidence": 0.5}, "x")

    def test_out_of_range_confidence_refused(self) -> None:
        with pytest.raises(UnclassifiedFigureError, match="within"):
            parse_figure({"value": 4, "evidence": "modeled", "confidence": 2.0}, "x")

    def test_error_names_the_offending_context(self) -> None:
        with pytest.raises(UnclassifiedFigureError, match="OPP-9.scores.alignment"):
            parse_figure(5, "OPP-9.scores.alignment")


class TestAggregation:
    def test_weakest_class_ordering(self) -> None:
        assert weakest([EvidenceClass.DOCUMENTED, EvidenceClass.MODELED]) is EvidenceClass.MODELED
        assert weakest([EvidenceClass.DOCUMENTED, EvidenceClass.ESTIMATED]) is EvidenceClass.ESTIMATED
        assert weakest([EvidenceClass.DOCUMENTED]) is EvidenceClass.DOCUMENTED

    def test_blending_cannot_launder_provenance(self) -> None:
        """One modeled input makes the aggregate modeled."""
        parts = [
            (0.9, Figure(5.0, EvidenceClass.DOCUMENTED, 0.9)),
            (0.1, Figure(1.0, EvidenceClass.MODELED, 0.4)),
        ]
        agg = weighted_aggregate(parts)
        assert agg.evidence is EvidenceClass.MODELED

    def test_weighted_value_and_confidence(self) -> None:
        parts = [
            (0.5, Figure(4.0, EvidenceClass.ESTIMATED, 0.8)),
            (0.5, Figure(2.0, EvidenceClass.ESTIMATED, 0.6)),
        ]
        agg = weighted_aggregate(parts)
        assert agg.value == pytest.approx(3.0)
        assert agg.confidence == pytest.approx(0.7)

    def test_derived_takes_minimum_confidence(self) -> None:
        inputs = [
            Figure(100.0, EvidenceClass.DOCUMENTED, 0.9),
            Figure(50.0, EvidenceClass.ESTIMATED, 0.6),
        ]
        result = derived(50.0, inputs)
        assert result.confidence == pytest.approx(0.6)
        assert result.evidence is EvidenceClass.ESTIMATED

    def test_empty_aggregate_rejected(self) -> None:
        with pytest.raises(ValueError):
            weighted_aggregate([])
        with pytest.raises(ValueError):
            derived(1.0, [])
        with pytest.raises(ValueError):
            weakest([])
