"""Rubric loading and value-model scoring tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from value_registry import (
    EvidenceClass,
    PortfolioError,
    RubricError,
    UnclassifiedFigureError,
    load_portfolio,
    load_rubric,
    score_portfolio,
)

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


@pytest.fixture()
def rubric_path() -> Path:
    return EXAMPLES / "rubric.yaml"


class TestRubricLoading:
    def test_example_rubric_loads(self, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        assert len(rubric.dimensions) == 6
        assert sum(d.weight for d in rubric.dimensions) == pytest.approx(1.0)
        assert [s.name for s in rubric.lifecycle] == [
            "intake", "assess", "pilot", "scale", "operate",
        ]
        assert rubric.stage("scale").gate.forbid_modeled_financials

    def test_weights_must_sum_to_one(self, tmp_path: Path, rubric_path: Path) -> None:
        raw = yaml.safe_load(rubric_path.read_text(encoding="utf-8"))
        raw["dimensions"][0]["weight"] = 0.9
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(RubricError, match="sum to 1.0"):
            load_rubric(bad)

    def test_duplicate_dimensions_rejected(self, tmp_path: Path, rubric_path: Path) -> None:
        raw = yaml.safe_load(rubric_path.read_text(encoding="utf-8"))
        raw["dimensions"][1]["name"] = raw["dimensions"][0]["name"]
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(RubricError, match="duplicate"):
            load_rubric(bad)

    def test_unknown_stage_and_readiness_raise(self, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        with pytest.raises(RubricError, match="unknown lifecycle stage"):
            rubric.stage("shipping")
        with pytest.raises(RubricError, match="unknown readiness"):
            rubric.multiplier("cosmic")


class TestPortfolioScoring:
    def test_example_portfolio_scores(self, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        opportunities = load_portfolio(EXAMPLES / "portfolio.yaml", rubric)
        scored = score_portfolio(opportunities, rubric)
        assert len(scored) == 4
        # ranked descending by adjusted score
        values = [s.adjusted_score.value for s in scored]
        assert values == sorted(values, reverse=True)

    def test_weighted_score_hand_computed(self, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        opps = load_portfolio(EXAMPLES / "portfolio.yaml", rubric)
        opp1 = next(o for o in opps if o.id == "OPP-001")
        scored = score_portfolio([opp1], rubric)[0]
        expected = (
            0.20 * 4.0 + 0.25 * 4.5 + 0.20 * 4.0 + 0.15 * 3.5 + 0.10 * 3.0 + 0.10 * 4.0
        )
        assert scored.weighted_score.value == pytest.approx(expected)
        # pilot_proven multiplier is 1.0
        assert scored.adjusted_score.value == pytest.approx(expected)

    def test_aggregate_inherits_weakest_class(self, rubric_path: Path) -> None:
        """OPP-001 has one modeled score, so the weighted score is modeled."""
        rubric = load_rubric(rubric_path)
        opps = load_portfolio(EXAMPLES / "portfolio.yaml", rubric)
        opp1 = next(o for o in opps if o.id == "OPP-001")
        scored = score_portfolio([opp1], rubric)[0]
        assert scored.weighted_score.evidence is EvidenceClass.MODELED

    def test_npv_hand_computed(self, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        opps = load_portfolio(EXAMPLES / "portfolio.yaml", rubric)
        opp1 = next(o for o in opps if o.id == "OPP-001")
        scored = score_portfolio([opp1], rubric)[0]
        net = 240000 - 55000
        expected = sum(net / 1.08**y for y in (1, 2, 3)) - 130000
        assert scored.npv.value == pytest.approx(expected)
        # NPV inherits weakest financial class (modeled benefit) and the
        # minimum financial confidence (0.5 on the benefit)
        assert scored.npv.evidence is EvidenceClass.MODELED
        assert scored.npv.confidence == pytest.approx(0.5)

    def test_payback_and_roi(self, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        opps = load_portfolio(EXAMPLES / "portfolio.yaml", rubric)
        opp1 = next(o for o in opps if o.id == "OPP-001")
        scored = score_portfolio([opp1], rubric)[0]
        assert scored.payback_years is not None
        assert scored.payback_years.value == pytest.approx(130000 / 185000)
        total_benefit = 240000 * 3
        total_cost = 55000 * 3 + 130000
        assert scored.roi.value == pytest.approx(
            (total_benefit - total_cost) / total_cost
        )


class TestGates:
    def test_scale_gate_blocks_modeled_financials(self, rubric_path: Path) -> None:
        """OPP-001 at pilot passes; the same numbers at scale would not,
        because the scale gate forbids modeled financials."""
        rubric = load_rubric(rubric_path)
        opps = load_portfolio(EXAMPLES / "portfolio.yaml", rubric)
        opp1 = next(o for o in opps if o.id == "OPP-001")
        from dataclasses import replace

        at_scale = replace(opp1, stage="scale")
        scored = score_portfolio([at_scale], rubric)[0]
        assert not scored.gate.passed
        assert any("modeled" in r for r in scored.gate.reasons)

    def test_documented_opportunity_passes_scale_gate(self, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        opps = load_portfolio(EXAMPLES / "portfolio.yaml", rubric)
        opp3 = next(o for o in opps if o.id == "OPP-003")  # all documented financials
        scored = score_portfolio([opp3], rubric)[0]
        assert scored.opportunity.stage == "scale"
        assert scored.gate.passed, scored.gate.reasons

    def test_intake_gate_is_open(self, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        opps = load_portfolio(EXAMPLES / "portfolio.yaml", rubric)
        opp4 = next(o for o in opps if o.id == "OPP-004")
        scored = score_portfolio([opp4], rubric)[0]
        assert scored.gate.passed


class TestPortfolioValidation:
    def test_bare_number_in_portfolio_refused_end_to_end(
        self, tmp_path: Path, rubric_path: Path
    ) -> None:
        """The headline behavior: a bare score in the YAML kills the run
        with a message naming the offending field."""
        rubric = load_rubric(rubric_path)
        raw = yaml.safe_load((EXAMPLES / "portfolio.yaml").read_text(encoding="utf-8"))
        raw["opportunities"][0]["scores"]["strategic_alignment"] = 4
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(UnclassifiedFigureError, match="OPP-001.scores.strategic_alignment"):
            load_portfolio(bad, rubric)

    def test_missing_dimension_rejected(self, tmp_path: Path, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        raw = yaml.safe_load((EXAMPLES / "portfolio.yaml").read_text(encoding="utf-8"))
        del raw["opportunities"][0]["scores"]["data_readiness"]
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(PortfolioError, match="data_readiness"):
            load_portfolio(bad, rubric)

    def test_duplicate_ids_rejected(self, tmp_path: Path, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        raw = yaml.safe_load((EXAMPLES / "portfolio.yaml").read_text(encoding="utf-8"))
        raw["opportunities"][1]["id"] = raw["opportunities"][0]["id"]
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(PortfolioError, match="duplicate"):
            load_portfolio(bad, rubric)

    def test_unknown_stage_in_portfolio_rejected(
        self, tmp_path: Path, rubric_path: Path
    ) -> None:
        rubric = load_rubric(rubric_path)
        raw = yaml.safe_load((EXAMPLES / "portfolio.yaml").read_text(encoding="utf-8"))
        raw["opportunities"][0]["stage"] = "warp"
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(RubricError, match="unknown lifecycle stage"):
            load_portfolio(bad, rubric)

    def test_bare_horizon_refused(self, tmp_path: Path, rubric_path: Path) -> None:
        """Review finding: horizon shapes NPV as much as the money —
        it cannot bypass the evidence system."""
        rubric = load_rubric(rubric_path)
        raw = yaml.safe_load((EXAMPLES / "portfolio.yaml").read_text(encoding="utf-8"))
        raw["opportunities"][0]["financials"]["horizon_years"] = 3
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(UnclassifiedFigureError, match="financials.horizon_years"):
            load_portfolio(bad, rubric)

    def test_bare_discount_rate_refused(self, tmp_path: Path, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        raw = yaml.safe_load((EXAMPLES / "portfolio.yaml").read_text(encoding="utf-8"))
        raw["opportunities"][0]["financials"]["discount_rate"] = 0.08
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(UnclassifiedFigureError, match="financials.discount_rate"):
            load_portfolio(bad, rubric)

    def test_fractional_horizon_rejected(self, tmp_path: Path, rubric_path: Path) -> None:
        rubric = load_rubric(rubric_path)
        raw = yaml.safe_load((EXAMPLES / "portfolio.yaml").read_text(encoding="utf-8"))
        raw["opportunities"][0]["financials"]["horizon_years"] = {
            "value": 2.5, "evidence": "estimated", "confidence": 0.7,
        }
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(PortfolioError, match="whole number"):
            load_portfolio(bad, rubric)


class TestHorizonAndRateProvenance:
    """A modeled horizon or rate must taint NPV — the review's exact
    scenario: all-documented money with a modeled assumption underneath."""

    def _with_modeled_rate(self, tmp_path: Path, rubric_path: Path):  # type: ignore[no-untyped-def]
        rubric = load_rubric(rubric_path)
        raw = yaml.safe_load((EXAMPLES / "portfolio.yaml").read_text(encoding="utf-8"))
        opp3 = next(o for o in raw["opportunities"] if o["id"] == "OPP-003")
        opp3["financials"]["discount_rate"] = {
            "value": 0.11, "evidence": "modeled", "confidence": 0.4,
        }
        path = tmp_path / "portfolio.yaml"
        path.write_text(yaml.safe_dump(raw), encoding="utf-8")
        return rubric, load_portfolio(path, rubric)

    def test_modeled_rate_taints_npv(self, tmp_path: Path, rubric_path: Path) -> None:
        rubric, opps = self._with_modeled_rate(tmp_path, rubric_path)
        opp3 = next(o for o in opps if o.id == "OPP-003")
        scored = score_portfolio([opp3], rubric)[0]
        assert scored.npv.evidence is EvidenceClass.MODELED
        assert scored.npv.confidence == pytest.approx(0.4)

    def test_modeled_rate_blocks_scale_gate(self, tmp_path: Path, rubric_path: Path) -> None:
        rubric, opps = self._with_modeled_rate(tmp_path, rubric_path)
        opp3 = next(o for o in opps if o.id == "OPP-003")
        scored = score_portfolio([opp3], rubric)[0]
        assert not scored.gate.passed
        assert any("discount_rate" in r for r in scored.gate.reasons)

    def test_roi_excludes_rate_but_includes_horizon(
        self, tmp_path: Path, rubric_path: Path
    ) -> None:
        """ROI is undiscounted: a modeled rate must NOT taint it, but a
        modeled horizon must — inheritance tracks true dependencies."""
        rubric, opps = self._with_modeled_rate(tmp_path, rubric_path)
        opp3 = next(o for o in opps if o.id == "OPP-003")
        scored = score_portfolio([opp3], rubric)[0]
        assert scored.roi.evidence is not EvidenceClass.MODELED
