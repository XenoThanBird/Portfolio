"""Evidence-classed figures — the shared data model and the point of
this package.

Every quantitative claim carries three things: its value, an **evidence
class** declaring how the number was obtained, and a **confidence**
in [0, 1]. The engine refuses to ingest or emit a bare number: an
unclassified figure raises :class:`UnclassifiedFigureError` instead of
flowing silently into a report.

Evidence classes, strongest to weakest:

- ``documented`` — traceable to a source record (invoice, telemetry,
  signed contract)
- ``estimated``  — derived by a person from partial data
- ``modeled``    — produced by an assumption-bearing model

Aggregation rules (used by scoring and risk engines):

- an aggregate's **class** is the *weakest* class among its inputs —
  one modeled input makes the aggregate modeled; blending cannot
  launder provenance
- weighted aggregates carry the weighted mean of input confidences;
  derived quantities (ROI, NPV) carry the *minimum* input confidence —
  a chain is no more certain than its least certain link
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple


class EvidenceClass(Enum):
    DOCUMENTED = "documented"
    ESTIMATED = "estimated"
    MODELED = "modeled"

    @property
    def strength(self) -> int:
        """Higher is stronger evidence."""
        return {"documented": 3, "estimated": 2, "modeled": 1}[self.value]


def weakest(classes: Sequence[EvidenceClass]) -> EvidenceClass:
    """The weakest evidence class present — aggregates inherit it."""
    if not classes:
        raise ValueError("cannot take weakest of no evidence classes")
    return min(classes, key=lambda c: c.strength)


class UnclassifiedFigureError(ValueError):
    """A number arrived without an evidence class and confidence."""


@dataclass(frozen=True)
class Figure:
    """A value that knows how it was obtained and how certain it is."""

    value: float
    evidence: EvidenceClass
    confidence: float
    unit: Optional[str] = None
    source: Optional[str] = None

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(
                f"confidence must be within [0, 1], got {self.confidence}"
            )

    def render(self, fmt: str = ",.2f") -> str:
        """Render value with its class and confidence — the only way
        figures appear in reports."""
        unit = f" {self.unit}" if self.unit else ""
        return (
            f"{self.value:{fmt}}{unit} "
            f"[{self.evidence.value}, conf {self.confidence:.2f}]"
        )

    def to_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {
            "value": self.value,
            "evidence": self.evidence.value,
            "confidence": self.confidence,
        }
        if self.unit is not None:
            d["unit"] = self.unit
        if self.source is not None:
            d["source"] = self.source
        return d


def parse_figure(raw: object, context: str) -> Figure:
    """Parse a figure from config input, refusing unclassified numbers.

    Accepts only a mapping with ``value``, ``evidence``, and
    ``confidence`` keys. A bare number — or a mapping missing its
    provenance — raises :class:`UnclassifiedFigureError` naming the
    offending field, which is the enforcement point for the
    no-unclassified-figures rule.
    """
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        raise UnclassifiedFigureError(
            f"{context}: bare number {raw!r} — every figure must declare "
            f"an evidence class (documented/estimated/modeled) and a confidence"
        )
    if not isinstance(raw, Mapping):
        raise UnclassifiedFigureError(
            f"{context}: expected a mapping with value/evidence/confidence, "
            f"got {type(raw).__name__}"
        )
    missing = [k for k in ("value", "evidence", "confidence") if k not in raw]
    if missing:
        raise UnclassifiedFigureError(
            f"{context}: figure is missing {', '.join(missing)}"
        )
    try:
        evidence = EvidenceClass(str(raw["evidence"]))
    except ValueError as exc:
        valid = ", ".join(c.value for c in EvidenceClass)
        raise UnclassifiedFigureError(
            f"{context}: unknown evidence class {raw['evidence']!r} "
            f"(valid: {valid})"
        ) from exc
    value = raw["value"]
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise UnclassifiedFigureError(f"{context}: value must be numeric")
    confidence = raw["confidence"]
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        raise UnclassifiedFigureError(f"{context}: confidence must be numeric")
    try:
        return Figure(
            value=float(value),
            evidence=evidence,
            confidence=float(confidence),
            unit=str(raw["unit"]) if "unit" in raw else None,
            source=str(raw["source"]) if "source" in raw else None,
        )
    except ValueError as exc:
        raise UnclassifiedFigureError(f"{context}: {exc}") from exc


def weighted_aggregate(
    parts: Sequence[Tuple[float, Figure]],
    unit: Optional[str] = None,
) -> Figure:
    """Aggregate (weight, figure) pairs into one figure.

    Value and confidence are weight-blended; the evidence class is the
    weakest class present, so blending cannot launder provenance.
    """
    if not parts:
        raise ValueError("cannot aggregate zero figures")
    total_weight = sum(w for w, _ in parts)
    if total_weight <= 0:
        raise ValueError("aggregate weights must sum to a positive number")
    value = sum(w * f.value for w, f in parts) / total_weight
    confidence = sum(w * f.confidence for w, f in parts) / total_weight
    evidence = weakest([f.evidence for _, f in parts])
    return Figure(value=value, evidence=evidence, confidence=confidence, unit=unit)


def derived(
    value: float,
    inputs: Sequence[Figure],
    unit: Optional[str] = None,
) -> Figure:
    """A quantity computed *from* figures (NPV, ROI, payback).

    Inherits the weakest input class and the minimum input confidence:
    a derivation is no more certain than its least certain input.
    """
    if not inputs:
        raise ValueError("a derived figure needs at least one input figure")
    return Figure(
        value=value,
        evidence=weakest([f.evidence for f in inputs]),
        confidence=min(f.confidence for f in inputs),
        unit=unit,
    )
