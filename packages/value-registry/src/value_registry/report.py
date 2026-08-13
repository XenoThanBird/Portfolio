"""Markdown report rendering.

Every quantitative cell is rendered through ``Figure.render()``, so the
evidence class and confidence appear beside every number. There is no
helper here that formats a bare float into a report — that is the
enforcement, by construction.
"""

from __future__ import annotations

from typing import Dict, List

from .evidence import Figure
from .registry import RISK_DIMENSIONS, RiskAssessment
from .rubric import Rubric
from .scoring import ScoredOpportunity

_LEGEND = (
    "> **Evidence legend** — every figure is rendered as "
    "`value [class, conf c]`, where class is `documented` (traceable to a "
    "source record), `estimated` (derived by a person from partial data), or "
    "`modeled` (produced by an assumption-bearing model), and `conf` is the "
    "declared confidence in [0, 1]. Aggregates inherit the weakest input "
    "class; derived quantities carry the minimum input confidence.\n"
)


def _fig(f: Figure, fmt: str = ",.2f") -> str:
    return f.render(fmt)


def render_portfolio_report(
    scored: List[ScoredOpportunity], rubric: Rubric
) -> str:
    """Portfolio scoring report: ranked table + per-opportunity detail."""
    lines: List[str] = []
    lines.append("# AI Opportunity Portfolio — Value Report")
    lines.append("")
    lines.append(f"Rubric: **{rubric.name}** ({len(rubric.dimensions)} dimensions)")
    lines.append("")
    lines.append(_LEGEND)

    lines.append("## Ranked portfolio")
    lines.append("")
    lines.append("| Rank | Opportunity | Stage | Adjusted score | NPV | ROI | Gate |")
    lines.append("| ---- | ---- | ---- | ---- | ---- | ---- | ---- |")
    for rank, s in enumerate(scored, start=1):
        gate = "PASS" if s.gate.passed else "HOLD"
        lines.append(
            f"| {rank} | {s.opportunity.name} ({s.opportunity.id}) "
            f"| {s.opportunity.stage} "
            f"| {_fig(s.adjusted_score)} "
            f"| {_fig(s.npv, ',.0f')} "
            f"| {_fig(s.roi, '.2f')} "
            f"| {gate} |"
        )
    lines.append("")

    lines.append("## Opportunity detail")
    for s in scored:
        o = s.opportunity
        lines.append("")
        lines.append(f"### {o.name} ({o.id})")
        lines.append("")
        lines.append(
            f"Value stream: `{o.value_stream}` · Stage: `{o.stage}` · "
            f"Readiness: `{o.readiness}` (×{s.readiness_multiplier:.2f})"
        )
        lines.append("")
        lines.append("| Dimension | Weight | Score |")
        lines.append("| ---- | ---- | ---- |")
        for dim in rubric.dimensions:
            lines.append(
                f"| {dim.name} | {dim.weight:.2f} | {_fig(o.scores[dim.name])} |"
            )
        lines.append(f"| **weighted** | 1.00 | {_fig(s.weighted_score)} |")
        lines.append("")
        lines.append(
            f"- Adjusted score (readiness ×{s.readiness_multiplier:.2f}): "
            f"{_fig(s.adjusted_score)}"
        )
        lines.append(f"- NPV over {o.financials.horizon_years}y "
                     f"@ {o.financials.discount_rate:.0%}: {_fig(s.npv, ',.0f')}")
        lines.append(f"- ROI: {_fig(s.roi, '.2f')}")
        if s.payback_years is not None:
            lines.append(f"- Payback: {_fig(s.payback_years, '.1f')}")
        else:
            lines.append("- Payback: not reached within horizon")
        gate_word = "passes" if s.gate.passed else "**does not pass**"
        lines.append(f"- Gate ({s.gate.stage}): {gate_word}")
        for reason in s.gate.reasons:
            lines.append(f"  - {reason}")
    lines.append("")
    return "\n".join(lines)


def render_registry_report(assessments: List[RiskAssessment]) -> str:
    """Model registry risk report with per-dimension confidence published."""
    lines: List[str] = []
    lines.append("# Model Registry — Risk Report")
    lines.append("")
    lines.append(
        f"{len(assessments)} models assessed. All entries are synthetic. "
        "Origin risk is rendered only as the generic "
        "**geopolitical-origin risk flag**."
    )
    lines.append("")
    lines.append(_LEGEND)

    flagged = [a for a in assessments if a.record.provenance.origin_risk_flag]
    states: Dict[str, int] = {}
    for a in assessments:
        states[a.record.approval_state.value] = (
            states.get(a.record.approval_state.value, 0) + 1
        )
    lines.append("## Inventory summary")
    lines.append("")
    lines.append(f"- Records: {len(assessments)}")
    lines.append(f"- Geopolitical-origin risk flag set: {len(flagged)}")
    lines.append(
        "- Approval states: "
        + ", ".join(f"{k}={v}" for k, v in sorted(states.items()))
    )
    lines.append("")

    lines.append("## Highest-risk models (top 15)")
    lines.append("")
    header = "| Model | Tier | Approval | Origin flag | Overall risk | " + " | ".join(
        dim.replace("_", " ") for dim in RISK_DIMENSIONS
    ) + " |"
    lines.append(header)
    lines.append("| ---- " * (5 + len(RISK_DIMENSIONS)) + "|")
    for a in assessments[:15]:
        r = a.record
        flag = "yes" if r.provenance.origin_risk_flag else "no"
        dims = " | ".join(_fig(a.dimensions[d], ".1f") for d in RISK_DIMENSIONS)
        lines.append(
            f"| {r.name} ({r.id}) | {r.tier} | {r.approval_state.value} "
            f"| {flag} | {_fig(a.overall, '.2f')} | {dims} |"
        )
    lines.append("")

    lines.append("## Review cadence exceptions")
    lines.append("")
    overdue_style = [
        a for a in assessments
        if a.overall.value >= 3.5 and a.record.review_cadence_days > 90
    ]
    if overdue_style:
        lines.append(
            "Models with overall risk ≥ 3.50 [see per-model evidence above] "
            "on a review cadence longer than 90 days:"
        )
        lines.append("")
        for a in overdue_style:
            lines.append(
                f"- {a.record.name} ({a.record.id}): overall "
                f"{_fig(a.overall, '.2f')}, cadence "
                f"{a.record.review_cadence_days}d"
            )
    else:
        lines.append("None — every high-risk model is on a ≤90-day cadence.")
    lines.append("")
    return "\n".join(lines)
