"""Registry schema, risk scoring, and synthetic catalog tests."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from value_registry import (
    RISK_DIMENSIONS,
    EvidenceClass,
    RegistryError,
    UnclassifiedFigureError,
    assess_catalog,
    assess_risk,
    generate_catalog,
    load_catalog,
    write_catalog,
)


@pytest.fixture()
def catalog_path(tmp_path: Path) -> Path:
    return write_catalog(tmp_path / "catalog.yaml", seed=7, count=25)


class TestCatalogGeneration:
    def test_fixed_seed_is_deterministic(self) -> None:
        assert generate_catalog(seed=42, count=30) == generate_catalog(seed=42, count=30)

    def test_different_seed_differs(self) -> None:
        assert generate_catalog(seed=1, count=30) != generate_catalog(seed=2, count=30)

    def test_default_count_is_140(self) -> None:
        data = generate_catalog()
        assert len(data["models"]) == 140

    def test_generated_catalog_validates_against_schema(self, catalog_path: Path) -> None:
        records = load_catalog(catalog_path)
        assert len(records) == 25
        assert all(set(r.risk) == set(RISK_DIMENSIONS) for r in records)

    def test_schema_has_no_concept_of_a_country(self, catalog_path: Path) -> None:
        """Origin risk is only ever the generic boolean flag."""
        raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
        for model in raw["models"]:
            provenance_keys = set(model["provenance"])
            assert provenance_keys == {"vendor", "origin_risk_flag", "open_weights", "hosting"}
            assert isinstance(model["provenance"]["origin_risk_flag"], bool)
        text = catalog_path.read_text(encoding="utf-8").lower()
        for word in ("country", "nation", "jurisdiction"):
            assert word not in text

    def test_disclaimer_present(self, catalog_path: Path) -> None:
        raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
        assert "fictional" in raw["disclaimer"]


class TestRegistryValidation:
    def test_bare_risk_number_refused(self, tmp_path: Path, catalog_path: Path) -> None:
        raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
        raw["models"][0]["risk"]["security"] = 3
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(UnclassifiedFigureError, match="risk.security"):
            load_catalog(bad)

    def test_risk_out_of_range_rejected(self, tmp_path: Path, catalog_path: Path) -> None:
        raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
        raw["models"][0]["risk"]["security"] = {
            "value": 9.0, "evidence": "estimated", "confidence": 0.5,
        }
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(RegistryError, match="within 1..5"):
            load_catalog(bad)

    def test_bad_tier_rejected(self, tmp_path: Path, catalog_path: Path) -> None:
        raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
        raw["models"][0]["tier"] = 7
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(RegistryError, match="tier"):
            load_catalog(bad)

    def test_unknown_approval_state_rejected(self, tmp_path: Path, catalog_path: Path) -> None:
        raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
        raw["models"][0]["approval_state"] = "vibes"
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(RegistryError, match="approval_state"):
            load_catalog(bad)

    def test_duplicate_ids_rejected(self, tmp_path: Path, catalog_path: Path) -> None:
        raw = yaml.safe_load(catalog_path.read_text(encoding="utf-8"))
        raw["models"][1]["id"] = raw["models"][0]["id"]
        bad = tmp_path / "bad.yaml"
        bad.write_text(yaml.safe_dump(raw), encoding="utf-8")
        with pytest.raises(RegistryError, match="duplicate"):
            load_catalog(bad)


class TestRiskScoring:
    def test_per_dimension_confidence_is_published(self, catalog_path: Path) -> None:
        records = load_catalog(catalog_path)
        assessment = assess_risk(records[0])
        assert set(assessment.dimensions) == set(RISK_DIMENSIONS)
        for fig in assessment.dimensions.values():
            assert 0.0 <= fig.confidence <= 1.0

    def test_equal_weight_overall_matches_mean(self, catalog_path: Path) -> None:
        records = load_catalog(catalog_path)
        a = assess_risk(records[0])
        mean = sum(f.value for f in records[0].risk.values()) / len(RISK_DIMENSIONS)
        assert a.overall.value == pytest.approx(mean)

    def test_overall_inherits_weakest_class(self, catalog_path: Path) -> None:
        records = load_catalog(catalog_path)
        a = assess_risk(records[0])
        weakest_strength = min(f.evidence.strength for f in records[0].risk.values())
        assert a.overall.evidence.strength == weakest_strength

    def test_custom_weights_change_overall(self, catalog_path: Path) -> None:
        records = load_catalog(catalog_path)
        record = records[0]
        security_only = assess_risk(record, weights={"security": 1.0})
        assert security_only.overall.value == pytest.approx(record.risk["security"].value)

    def test_unknown_weight_dimension_rejected(self, catalog_path: Path) -> None:
        records = load_catalog(catalog_path)
        with pytest.raises(RegistryError, match="unknown risk weight"):
            assess_risk(records[0], weights={"astrology": 1.0})

    def test_catalog_assessment_ranked_descending(self, catalog_path: Path) -> None:
        records = load_catalog(catalog_path)
        assessments = assess_catalog(records)
        values = [a.overall.value for a in assessments]
        assert values == sorted(values, reverse=True)

    def test_class_never_stronger_than_weakest_input(self, catalog_path: Path) -> None:
        """Property over the whole synthetic catalog: no overall risk
        figure claims stronger evidence than its weakest dimension."""
        for a in assess_catalog(load_catalog(catalog_path)):
            weakest_strength = min(f.evidence.strength for f in a.dimensions.values())
            assert a.overall.evidence.strength == weakest_strength
