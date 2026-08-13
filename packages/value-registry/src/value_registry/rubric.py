"""Rubric and lifecycle configuration — declared in YAML, never hardcoded.

A rubric names its scoring dimensions and weights (which must sum to
1.0), the readiness multipliers, and a staged lifecycle where each
stage carries entry/exit criteria and a machine-checkable gate.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Union

import yaml

WEIGHT_TOLERANCE = 1e-6


class RubricError(ValueError):
    """Raised when a rubric file is structurally invalid."""


@dataclass(frozen=True)
class Dimension:
    name: str
    weight: float
    description: str = ""


@dataclass(frozen=True)
class Gate:
    """Machine-checkable gate thresholds for one lifecycle stage."""

    min_score: float = 0.0
    min_confidence: float = 0.0
    forbid_modeled_financials: bool = False


@dataclass(frozen=True)
class Stage:
    name: str
    entry_criteria: List[str] = field(default_factory=list)
    exit_criteria: List[str] = field(default_factory=list)
    gate: Gate = field(default_factory=Gate)


@dataclass(frozen=True)
class Rubric:
    name: str
    dimensions: List[Dimension]
    readiness_multipliers: Dict[str, float]
    lifecycle: List[Stage]

    def dimension_names(self) -> List[str]:
        return [d.name for d in self.dimensions]

    def stage(self, name: str) -> Stage:
        for stage in self.lifecycle:
            if stage.name == name:
                return stage
        valid = ", ".join(s.name for s in self.lifecycle)
        raise RubricError(f"unknown lifecycle stage {name!r} (valid: {valid})")

    def multiplier(self, readiness: str) -> float:
        if readiness not in self.readiness_multipliers:
            valid = ", ".join(sorted(self.readiness_multipliers))
            raise RubricError(
                f"unknown readiness level {readiness!r} (valid: {valid})"
            )
        return self.readiness_multipliers[readiness]


def _require(mapping: Mapping[str, Any], key: str, context: str) -> Any:
    if key not in mapping:
        raise RubricError(f"{context}: missing required key {key!r}")
    return mapping[key]


def load_rubric(path: Union[str, Path]) -> Rubric:
    """Load and validate a rubric YAML file."""
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise RubricError(f"{path}: rubric file must be a mapping")

    name = str(_require(raw, "name", str(path)))

    dims_raw = _require(raw, "dimensions", str(path))
    if not isinstance(dims_raw, list) or not dims_raw:
        raise RubricError(f"{path}: dimensions must be a non-empty list")
    dimensions = []
    for i, d in enumerate(dims_raw):
        if not isinstance(d, Mapping):
            raise RubricError(f"{path}: dimensions[{i}] must be a mapping")
        dimensions.append(
            Dimension(
                name=str(_require(d, "name", f"dimensions[{i}]")),
                weight=float(_require(d, "weight", f"dimensions[{i}]")),
                description=str(d.get("description", "")),
            )
        )
    names = [d.name for d in dimensions]
    if len(set(names)) != len(names):
        raise RubricError(f"{path}: duplicate dimension names")
    total = sum(d.weight for d in dimensions)
    if abs(total - 1.0) > WEIGHT_TOLERANCE:
        raise RubricError(
            f"{path}: dimension weights must sum to 1.0, got {total:.6f}"
        )
    if any(d.weight <= 0 for d in dimensions):
        raise RubricError(f"{path}: dimension weights must be positive")

    mult_raw = _require(raw, "readiness_multipliers", str(path))
    if not isinstance(mult_raw, Mapping) or not mult_raw:
        raise RubricError(f"{path}: readiness_multipliers must be a non-empty mapping")
    multipliers = {str(k): float(v) for k, v in mult_raw.items()}
    if any(v <= 0 for v in multipliers.values()):
        raise RubricError(f"{path}: readiness multipliers must be positive")

    stages_raw = _require(raw, "lifecycle", str(path))
    if not isinstance(stages_raw, list) or not stages_raw:
        raise RubricError(f"{path}: lifecycle must be a non-empty list of stages")
    stages = []
    for i, s in enumerate(stages_raw):
        if not isinstance(s, Mapping):
            raise RubricError(f"{path}: lifecycle[{i}] must be a mapping")
        gate_raw: Mapping[str, Any] = s.get("gate") or {}
        if not isinstance(gate_raw, Mapping):
            raise RubricError(f"{path}: lifecycle[{i}].gate must be a mapping")
        stages.append(
            Stage(
                name=str(_require(s, "stage", f"lifecycle[{i}]")),
                entry_criteria=[str(c) for c in (s.get("entry") or [])],
                exit_criteria=[str(c) for c in (s.get("exit") or [])],
                gate=Gate(
                    min_score=float(gate_raw.get("min_score", 0.0)),
                    min_confidence=float(gate_raw.get("min_confidence", 0.0)),
                    forbid_modeled_financials=bool(
                        gate_raw.get("forbid_modeled_financials", False)
                    ),
                ),
            )
        )
    stage_names = [s.name for s in stages]
    if len(set(stage_names)) != len(stage_names):
        raise RubricError(f"{path}: duplicate lifecycle stage names")

    return Rubric(
        name=name,
        dimensions=dimensions,
        readiness_multipliers=multipliers,
        lifecycle=stages,
    )
