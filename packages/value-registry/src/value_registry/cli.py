"""Command-line interface.

Subcommands:

- ``score``            — score a portfolio YAML against a rubric YAML,
                         emit a markdown report
- ``generate-catalog`` — write the fixed-seed synthetic model catalog
- ``registry-report``  — assess a catalog, emit a markdown risk report
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .catalog import DEFAULT_COUNT, DEFAULT_SEED, write_catalog
from .registry import assess_catalog, load_catalog
from .report import render_portfolio_report, render_registry_report
from .rubric import load_rubric
from .scoring import load_portfolio, score_portfolio


def _write_or_print(text: str, out: Optional[str]) -> None:
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(text, encoding="utf-8", newline="\n")
        print(f"wrote {out}")
    else:
        print(text)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="value-registry",
        description="AI opportunity value model + model registry "
        "with mandatory evidence-class labeling.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_score = sub.add_parser("score", help="score a portfolio against a rubric")
    p_score.add_argument("--rubric", required=True, help="rubric YAML path")
    p_score.add_argument("--portfolio", required=True, help="portfolio YAML path")
    p_score.add_argument("--out", help="output markdown path (default: stdout)")

    p_gen = sub.add_parser(
        "generate-catalog", help="write the synthetic model catalog"
    )
    p_gen.add_argument("--out", required=True, help="output YAML path")
    p_gen.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p_gen.add_argument("--count", type=int, default=DEFAULT_COUNT)

    p_reg = sub.add_parser(
        "registry-report", help="assess a catalog and emit a risk report"
    )
    p_reg.add_argument("--catalog", required=True, help="catalog YAML path")
    p_reg.add_argument("--out", help="output markdown path (default: stdout)")

    args = parser.parse_args(argv)

    if args.command == "score":
        rubric = load_rubric(args.rubric)
        opportunities = load_portfolio(args.portfolio, rubric)
        scored = score_portfolio(opportunities, rubric)
        _write_or_print(render_portfolio_report(scored, rubric), args.out)
        return 0

    if args.command == "generate-catalog":
        path = write_catalog(args.out, seed=args.seed, count=args.count)
        print(f"wrote {path} (seed={args.seed}, count={args.count})")
        return 0

    if args.command == "registry-report":
        records = load_catalog(args.catalog)
        assessments = assess_catalog(records)
        _write_or_print(render_registry_report(assessments), args.out)
        return 0

    return 2  # pragma: no cover — argparse enforces the subcommands


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
