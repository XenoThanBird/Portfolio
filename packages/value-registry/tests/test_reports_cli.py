"""Report rendering and CLI end-to-end tests."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from value_registry import (
    assess_catalog,
    load_catalog,
    load_portfolio,
    load_rubric,
    render_portfolio_report,
    render_registry_report,
    score_portfolio,
    write_catalog,
)
from value_registry.cli import main

EXAMPLES = Path(__file__).resolve().parents[1] / "examples"

FIGURE_MARKER = re.compile(r"\[(documented|estimated|modeled), conf 0\.\d{2}\]")


class TestPortfolioReport:
    @pytest.fixture()
    def report(self) -> str:
        rubric = load_rubric(EXAMPLES / "rubric.yaml")
        scored = score_portfolio(load_portfolio(EXAMPLES / "portfolio.yaml", rubric), rubric)
        return render_portfolio_report(scored, rubric)

    def test_every_ranked_row_carries_evidence_markers(self, report: str) -> None:
        """Every numeric column in the ranked table renders class +
        confidence: 3 figures per row (adjusted, NPV, ROI)."""
        rows = [
            line for line in report.splitlines()
            if line.startswith("| ") and "OPP-" in line and "| Rank" not in line
        ]
        assert rows
        for row in rows:
            assert len(FIGURE_MARKER.findall(row)) >= 3, row

    def test_detail_scores_all_marked(self, report: str) -> None:
        # 4 opportunities × (6 dimensions + weighted) plus summary bullets
        assert len(FIGURE_MARKER.findall(report)) >= 4 * 7

    def test_legend_present(self, report: str) -> None:
        assert "Evidence legend" in report
        assert "documented" in report and "modeled" in report

    def test_gate_holds_are_visible(self, report: str) -> None:
        assert "PASS" in report  # at least one passing gate in the table


class TestRegistryReport:
    def test_report_publishes_dimension_confidences(self, tmp_path: Path) -> None:
        path = write_catalog(tmp_path / "catalog.yaml", seed=7, count=25)
        assessments = assess_catalog(load_catalog(path))
        report = render_registry_report(assessments)
        assert "geopolitical-origin risk flag" in report
        # top-15 table rows: overall + 5 dimensions all marked
        rows = [line for line in report.splitlines() if line.startswith("| ") and "MDL-" in line]
        assert len(rows) == 15
        for row in rows:
            assert len(FIGURE_MARKER.findall(row)) == 6, row

    def test_no_countries_in_report(self, tmp_path: Path) -> None:
        path = write_catalog(tmp_path / "catalog.yaml", seed=7, count=25)
        report = render_registry_report(assess_catalog(load_catalog(path)))
        assert "country" not in report.lower()


class TestCLI:
    def test_score_end_to_end(self, tmp_path: Path) -> None:
        out = tmp_path / "portfolio_report.md"
        rc = main([
            "score",
            "--rubric", str(EXAMPLES / "rubric.yaml"),
            "--portfolio", str(EXAMPLES / "portfolio.yaml"),
            "--out", str(out),
        ])
        assert rc == 0
        assert "Ranked portfolio" in out.read_text(encoding="utf-8")

    def test_generate_and_report_end_to_end(self, tmp_path: Path) -> None:
        catalog = tmp_path / "catalog.yaml"
        report = tmp_path / "registry_report.md"
        assert main(["generate-catalog", "--out", str(catalog), "--seed", "9", "--count", "20"]) == 0
        assert main(["registry-report", "--catalog", str(catalog), "--out", str(report)]) == 0
        text = report.read_text(encoding="utf-8")
        assert "20 models assessed" in text

    def test_score_to_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        rc = main([
            "score",
            "--rubric", str(EXAMPLES / "rubric.yaml"),
            "--portfolio", str(EXAMPLES / "portfolio.yaml"),
        ])
        assert rc == 0
        assert "Ranked portfolio" in capsys.readouterr().out
