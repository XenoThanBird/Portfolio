"""AI opportunity value model: weighted scoring, readiness multiplier,
ROI/NPV, and lifecycle gate evaluation.

Every quantitative input must arrive as an evidence-classed figure
(see :mod:`value_registry.evidence`); every quantitative output leaves
as one. There is no code path from a bare number to a report.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

import yaml

from .evidence import (
    EvidenceClass,
    Figure,
    UnclassifiedFigureError,
    derived,
    parse_figure,
    weighted_aggregate,
)
from .rubric import Rubric, RubricError, Stage


@dataclass(frozen=True)
class Financials:
    """All five NPV inputs are evidence-classed — including the horizon
    and discount rate, which shape NPV as much as the monetary figures
    and must not be able to hide behind them."""

    annual_benefit: Figure
    annual_run_cost: Figure
    implementation_cost: Figure
    horizon_years: Figure
    discount_rate: Figure

    def horizon(self) -> int:
        return int(self.horizon_years.value)

    def monetary_figures(self) -> List[Figure]:
        return [self.annual_benefit, self.annual_run_cost, self.implementation_cost]

    def all_figures(self) -> List[Figure]:
        return self.monetary_figures() + [self.horizon_years, self.discount_rate]


@dataclass(frozen=True)
class Opportunity:
    id: str
    name: str
    value_stream: str
    stage: str
    readiness: str
    scores: Dict[str, Figure]
    financials: Financials


@dataclass(frozen=True)
class GateResult:
    stage: str
    passed: bool
    reasons: List[str]


@dataclass(frozen=True)
class ScoredOpportunity:
    opportunity: Opportunity
    weighted_score: Figure
    adjusted_score: Figure  # weighted * readiness multiplier
    readiness_multiplier: float
    npv: Figure
    roi: Figure
    payback_years: Optional[Figure]  # None when never paid back in horizon
    gate: GateResult


class PortfolioError(ValueError):
    """Raised when a portfolio file is structurally invalid."""


def _parse_opportunity(raw: Mapping[str, Any], rubric: Rubric, idx: int) -> Opportunity:
    ctx = f"opportunities[{idx}]"
    for key in ("id", "name", "value_stream", "stage", "readiness", "scores", "financials"):
        if key not in raw:
            raise PortfolioError(f"{ctx}: missing required key {key!r}")

    opp_id = str(raw["id"])
    scores_raw = raw["scores"]
    if not isinstance(scores_raw, Mapping):
        raise PortfolioError(f"{ctx}: scores must be a mapping")
    scores: Dict[str, Figure] = {}
    for dim in rubric.dimensions:
        if dim.name not in scores_raw:
            raise PortfolioError(
                f"{ctx} ({opp_id}): missing score for dimension {dim.name!r}"
            )
        scores[dim.name] = parse_figure(
            scores_raw[dim.name], f"{opp_id}.scores.{dim.name}"
        )
    extras = set(scores_raw) - set(rubric.dimension_names())
    if extras:
        raise PortfolioError(
            f"{ctx} ({opp_id}): scores for unknown dimensions: {sorted(extras)}"
        )

    fin_raw = raw["financials"]
    if not isinstance(fin_raw, Mapping):
        raise PortfolioError(f"{ctx}: financials must be a mapping")
    for key in ("annual_benefit", "annual_run_cost", "implementation_cost",
                "horizon_years", "discount_rate"):
        if key not in fin_raw:
            raise PortfolioError(f"{ctx} ({opp_id}): financials missing {key!r}")
    financials = Financials(
        annual_benefit=parse_figure(fin_raw["annual_benefit"], f"{opp_id}.financials.annual_benefit"),
        annual_run_cost=parse_figure(fin_raw["annual_run_cost"], f"{opp_id}.financials.annual_run_cost"),
        implementation_cost=parse_figure(fin_raw["implementation_cost"], f"{opp_id}.financials.implementation_cost"),
        horizon_years=parse_figure(fin_raw["horizon_years"], f"{opp_id}.financials.horizon_years"),
        discount_rate=parse_figure(fin_raw["discount_rate"], f"{opp_id}.financials.discount_rate"),
    )
    horizon = financials.horizon_years.value
    if horizon < 1 or horizon != int(horizon):
        raise PortfolioError(
            f"{ctx} ({opp_id}): horizon_years value must be a whole number >= 1"
        )
    if financials.discount_rate.value < 0:
        raise PortfolioError(f"{ctx} ({opp_id}): discount_rate must be >= 0")

    stage = str(raw["stage"])
    rubric.stage(stage)  # validates the stage exists
    readiness = str(raw["readiness"])
    rubric.multiplier(readiness)  # validates the readiness level exists

    return Opportunity(
        id=opp_id,
        name=str(raw["name"]),
        value_stream=str(raw["value_stream"]),
        stage=stage,
        readiness=readiness,
        scores=scores,
        financials=financials,
    )


def load_portfolio(path: Union[str, Path], rubric: Rubric) -> List[Opportunity]:
    """Load and validate a portfolio YAML file against a rubric."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping) or "opportunities" not in raw:
        raise PortfolioError(f"{path}: portfolio file must contain 'opportunities'")
    opps_raw = raw["opportunities"]
    if not isinstance(opps_raw, list) or not opps_raw:
        raise PortfolioError(f"{path}: opportunities must be a non-empty list")
    opportunities = [
        _parse_opportunity(o, rubric, i) for i, o in enumerate(opps_raw)
    ]
    ids = [o.id for o in opportunities]
    if len(set(ids)) != len(ids):
        raise PortfolioError(f"{path}: duplicate opportunity ids")
    return opportunities


def _npv(fin: Financials) -> float:
    """NPV of (benefit - run cost) over the horizon, less implementation."""
    net_annual = fin.annual_benefit.value - fin.annual_run_cost.value
    discounted = sum(
        net_annual / (1.0 + fin.discount_rate.value) ** year
        for year in range(1, fin.horizon() + 1)
    )
    return discounted - fin.implementation_cost.value


def _payback_years(fin: Financials) -> Optional[float]:
    """Undiscounted years to recover implementation cost, or None."""
    net_annual = fin.annual_benefit.value - fin.annual_run_cost.value
    if net_annual <= 0:
        return None
    years = fin.implementation_cost.value / net_annual
    return years if years <= fin.horizon() else None


def _evaluate_gate(
    stage: Stage,
    adjusted: Figure,
    financials: Financials,
) -> GateResult:
    reasons: List[str] = []
    if adjusted.value < stage.gate.min_score:
        reasons.append(
            f"adjusted score {adjusted.value:.2f} below gate minimum "
            f"{stage.gate.min_score:.2f}"
        )
    if adjusted.confidence < stage.gate.min_confidence:
        reasons.append(
            f"aggregate confidence {adjusted.confidence:.2f} below gate "
            f"minimum {stage.gate.min_confidence:.2f}"
        )
    if stage.gate.forbid_modeled_financials:
        modeled = [
            name
            for name, fig in (
                ("annual_benefit", financials.annual_benefit),
                ("annual_run_cost", financials.annual_run_cost),
                ("implementation_cost", financials.implementation_cost),
                ("horizon_years", financials.horizon_years),
                ("discount_rate", financials.discount_rate),
            )
            if fig.evidence is EvidenceClass.MODELED
        ]
        if modeled:
            reasons.append(
                f"gate forbids modeled financials; still modeled: {', '.join(modeled)}"
            )
    return GateResult(stage=stage.name, passed=not reasons, reasons=reasons)


def score_opportunity(opp: Opportunity, rubric: Rubric) -> ScoredOpportunity:
    """Score one opportunity: weighted score, readiness adjustment,
    ROI/NPV, and its current stage's gate."""
    parts = [(d.weight, opp.scores[d.name]) for d in rubric.dimensions]
    weighted = weighted_aggregate(parts)

    multiplier = rubric.multiplier(opp.readiness)
    adjusted = Figure(
        value=weighted.value * multiplier,
        evidence=weighted.evidence,
        confidence=weighted.confidence,
    )

    fin = opp.financials
    # NPV depends on every financial input incl. horizon and rate; ROI
    # and payback on the monetary figures plus the horizon. Provenance
    # inheritance covers exactly the inputs each quantity depends on.
    npv = derived(_npv(fin), fin.all_figures(), unit=fin.annual_benefit.unit)

    roi_inputs = fin.monetary_figures() + [fin.horizon_years]
    total_benefit = fin.annual_benefit.value * fin.horizon()
    total_cost = (
        fin.annual_run_cost.value * fin.horizon()
        + fin.implementation_cost.value
    )
    if total_cost <= 0:
        raise PortfolioError(f"{opp.id}: total cost must be positive to compute ROI")
    roi = derived((total_benefit - total_cost) / total_cost, roi_inputs)

    payback_raw = _payback_years(fin)
    payback = (
        derived(payback_raw, roi_inputs, unit="years")
        if payback_raw is not None
        else None
    )

    gate = _evaluate_gate(rubric.stage(opp.stage), adjusted, fin)

    return ScoredOpportunity(
        opportunity=opp,
        weighted_score=weighted,
        adjusted_score=adjusted,
        readiness_multiplier=multiplier,
        npv=npv,
        roi=roi,
        payback_years=payback,
        gate=gate,
    )


def score_portfolio(
    opportunities: List[Opportunity], rubric: Rubric
) -> List[ScoredOpportunity]:
    """Score every opportunity, ranked by adjusted score (descending)."""
    scored = [score_opportunity(o, rubric) for o in opportunities]
    return sorted(scored, key=lambda s: s.adjusted_score.value, reverse=True)
