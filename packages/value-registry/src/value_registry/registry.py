"""Model registry & third-party risk (TPRM) schema.

Each model inventory record carries: capability tier, provenance (with
a generic **geopolitical-origin risk flag** — the schema never names
countries, by design), value stream, approval state, review cadence,
and per-dimension risk scores as evidence-classed figures.

Risk scoring publishes the confidence of every dimension in its output
— the confidence values are part of the deliverable, not an
implementation detail.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

import yaml

from .evidence import Figure, parse_figure, weighted_aggregate

RISK_DIMENSIONS = (
    "security",
    "data_privacy",
    "operational",
    "geopolitical_origin",
    "vendor_concentration",
)


class ApprovalState(Enum):
    PROPOSED = "proposed"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    CONDITIONAL = "conditional"
    REJECTED = "rejected"
    RETIRED = "retired"


class Hosting(Enum):
    SAAS = "saas"
    SELF_HOSTED = "self_hosted"
    ON_PREM = "on_prem"


class RegistryError(ValueError):
    """Raised when a catalog file is structurally invalid."""


@dataclass(frozen=True)
class Provenance:
    vendor: str
    origin_risk_flag: bool  # geopolitical-origin risk flag — generic by design
    open_weights: bool
    hosting: Hosting


@dataclass(frozen=True)
class ModelRecord:
    id: str
    name: str
    tier: int  # 1 (experimental) .. 4 (business-critical)
    value_stream: str
    approval_state: ApprovalState
    review_cadence_days: int
    provenance: Provenance
    risk: Dict[str, Figure]  # keyed by RISK_DIMENSIONS


@dataclass(frozen=True)
class RiskAssessment:
    """Overall risk plus the published per-dimension figures."""

    record: ModelRecord
    overall: Figure
    dimensions: Dict[str, Figure] = field(default_factory=dict)


def _parse_record(raw: Mapping[str, Any], idx: int) -> ModelRecord:
    ctx = f"models[{idx}]"
    for key in ("id", "name", "tier", "value_stream", "approval_state",
                "review_cadence_days", "provenance", "risk"):
        if key not in raw:
            raise RegistryError(f"{ctx}: missing required key {key!r}")
    model_id = str(raw["id"])

    tier = int(raw["tier"])
    if not 1 <= tier <= 4:
        raise RegistryError(f"{ctx} ({model_id}): tier must be 1..4, got {tier}")

    try:
        approval = ApprovalState(str(raw["approval_state"]))
    except ValueError as exc:
        valid = ", ".join(s.value for s in ApprovalState)
        raise RegistryError(
            f"{ctx} ({model_id}): unknown approval_state (valid: {valid})"
        ) from exc

    cadence = int(raw["review_cadence_days"])
    if cadence < 1:
        raise RegistryError(f"{ctx} ({model_id}): review_cadence_days must be >= 1")

    prov_raw = raw["provenance"]
    if not isinstance(prov_raw, Mapping):
        raise RegistryError(f"{ctx} ({model_id}): provenance must be a mapping")
    for key in ("vendor", "origin_risk_flag", "open_weights", "hosting"):
        if key not in prov_raw:
            raise RegistryError(f"{ctx} ({model_id}): provenance missing {key!r}")
    try:
        hosting = Hosting(str(prov_raw["hosting"]))
    except ValueError as exc:
        valid = ", ".join(h.value for h in Hosting)
        raise RegistryError(
            f"{ctx} ({model_id}): unknown hosting (valid: {valid})"
        ) from exc
    provenance = Provenance(
        vendor=str(prov_raw["vendor"]),
        origin_risk_flag=bool(prov_raw["origin_risk_flag"]),
        open_weights=bool(prov_raw["open_weights"]),
        hosting=hosting,
    )

    risk_raw = raw["risk"]
    if not isinstance(risk_raw, Mapping):
        raise RegistryError(f"{ctx} ({model_id}): risk must be a mapping")
    risk: Dict[str, Figure] = {}
    for dim in RISK_DIMENSIONS:
        if dim not in risk_raw:
            raise RegistryError(f"{ctx} ({model_id}): risk missing dimension {dim!r}")
        fig = parse_figure(risk_raw[dim], f"{model_id}.risk.{dim}")
        if not 1.0 <= fig.value <= 5.0:
            raise RegistryError(
                f"{ctx} ({model_id}): risk.{dim} must be within 1..5, got {fig.value}"
            )
        risk[dim] = fig
    extras = set(risk_raw) - set(RISK_DIMENSIONS)
    if extras:
        raise RegistryError(
            f"{ctx} ({model_id}): unknown risk dimensions: {sorted(extras)}"
        )

    return ModelRecord(
        id=model_id,
        name=str(raw["name"]),
        tier=tier,
        value_stream=str(raw["value_stream"]),
        approval_state=approval,
        review_cadence_days=cadence,
        provenance=provenance,
        risk=risk,
    )


def load_catalog(path: Union[str, Path]) -> List[ModelRecord]:
    """Load and validate a model catalog YAML file."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping) or "models" not in raw:
        raise RegistryError(f"{path}: catalog file must contain 'models'")
    models_raw = raw["models"]
    if not isinstance(models_raw, list) or not models_raw:
        raise RegistryError(f"{path}: models must be a non-empty list")
    records = [_parse_record(m, i) for i, m in enumerate(models_raw)]
    ids = [r.id for r in records]
    if len(set(ids)) != len(ids):
        raise RegistryError(f"{path}: duplicate model ids")
    return records


def assess_risk(
    record: ModelRecord,
    weights: Optional[Dict[str, float]] = None,
) -> RiskAssessment:
    """Score one record's overall risk.

    ``weights`` maps risk dimensions to weights (default: equal). The
    per-dimension figures — including their confidences — are part of
    the returned assessment, not just the blended overall number.
    """
    if weights is None:
        weights = {dim: 1.0 for dim in RISK_DIMENSIONS}
    unknown = set(weights) - set(RISK_DIMENSIONS)
    if unknown:
        raise RegistryError(f"unknown risk weight dimensions: {sorted(unknown)}")
    parts = [(weights.get(dim, 0.0), record.risk[dim]) for dim in RISK_DIMENSIONS]
    overall = weighted_aggregate([(w, f) for w, f in parts if w > 0])
    return RiskAssessment(record=record, overall=overall, dimensions=dict(record.risk))


def assess_catalog(
    records: List[ModelRecord],
    weights: Optional[Dict[str, float]] = None,
) -> List[RiskAssessment]:
    """Assess every record, ranked by overall risk (descending)."""
    assessments = [assess_risk(r, weights) for r in records]
    return sorted(assessments, key=lambda a: a.overall.value, reverse=True)
