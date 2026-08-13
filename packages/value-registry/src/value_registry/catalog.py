"""Synthetic model catalog generator.

Produces ~140 fictional model inventory entries from a fixed seed —
same seed, same catalog, byte for byte. Every vendor and model name is
assembled from fictional word lists; no real vendors, no real models,
and (by schema design) no countries anywhere: origin risk is only ever
the generic boolean **geopolitical-origin risk flag**.
"""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml

from .registry import RISK_DIMENSIONS, ApprovalState, Hosting

DEFAULT_SEED = 42
DEFAULT_COUNT = 140

_VENDOR_FIRST = [
    "Bluewater", "Quartzline", "Fernwood", "Halcyon", "Ironvale", "Juniper",
    "Kestrel", "Larkspur", "Marrowbay", "Nightfall", "Opaline", "Pinegate",
]
_VENDOR_SECOND = [
    "Analytics", "Cognition", "Dynamics", "Foundry", "Intelligence", "Labs",
    "Logic", "Minds", "Networks", "Systems",
]
_MODEL_FIRST = [
    "Aster", "Basalt", "Cinder", "Drift", "Ember", "Flint", "Garnet",
    "Harbor", "Isle", "Juno", "Krait", "Lumen", "Mesa", "Nimbus",
]
_MODEL_SECOND = [
    "Chat", "Classify", "Extract", "Forecast", "Rank", "Reason",
    "Summarize", "Translate", "Vision", "Voice",
]
_MODEL_SIZE = ["Nano", "Small", "Base", "Large", "Ultra"]
_VALUE_STREAMS = [
    "customer_operations", "field_operations", "engineering", "finance",
    "supply_chain", "workforce_enablement", "safety_compliance",
]
_EVIDENCE = ["documented", "estimated", "modeled"]


def _risk_figure(rng: random.Random) -> Dict[str, Any]:
    evidence = rng.choices(_EVIDENCE, weights=[3, 4, 2])[0]
    confidence = {
        "documented": rng.uniform(0.75, 0.98),
        "estimated": rng.uniform(0.5, 0.8),
        "modeled": rng.uniform(0.3, 0.6),
    }[evidence]
    return {
        "value": round(rng.uniform(1.0, 5.0), 1),
        "evidence": evidence,
        "confidence": round(confidence, 2),
    }


def generate_catalog(
    seed: int = DEFAULT_SEED, count: int = DEFAULT_COUNT
) -> Dict[str, Any]:
    """Generate a deterministic synthetic catalog as plain data."""
    rng = random.Random(seed)
    models: List[Dict[str, Any]] = []
    for i in range(count):
        vendor = f"{rng.choice(_VENDOR_FIRST)} {rng.choice(_VENDOR_SECOND)}"
        name = (
            f"{rng.choice(_MODEL_FIRST)}-{rng.choice(_MODEL_SECOND)}-"
            f"{rng.choice(_MODEL_SIZE)}"
        )
        models.append(
            {
                "id": f"MDL-{i + 1:04d}",
                "name": name,
                "tier": rng.choices([1, 2, 3, 4], weights=[3, 4, 2, 1])[0],
                "value_stream": rng.choice(_VALUE_STREAMS),
                "approval_state": rng.choices(
                    [s.value for s in ApprovalState],
                    weights=[3, 3, 6, 2, 1, 1],
                )[0],
                "review_cadence_days": rng.choice([30, 60, 90, 180, 365]),
                "provenance": {
                    "vendor": vendor,
                    # Generic geopolitical-origin risk flag; the schema
                    # deliberately has no concept of a country.
                    "origin_risk_flag": rng.random() < 0.15,
                    "open_weights": rng.random() < 0.4,
                    "hosting": rng.choice([h.value for h in Hosting]),
                },
                "risk": {dim: _risk_figure(rng) for dim in RISK_DIMENSIONS},
            }
        )
    return {
        "catalog": "synthetic-model-inventory",
        "disclaimer": (
            "All entries are fictional and generated with a fixed seed. "
            "No real vendors, models, or organizations are described."
        ),
        "seed": seed,
        "models": models,
    }


def write_catalog(
    path: Union[str, Path],
    seed: int = DEFAULT_SEED,
    count: int = DEFAULT_COUNT,
) -> Path:
    """Generate and write the catalog YAML; returns the path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    data = generate_catalog(seed=seed, count=count)
    out.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )
    return out
