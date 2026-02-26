"""
Report Generator
-----------------
Post-mission report generation in Markdown and JSON formats.
Reads mission_result.json and produces a human-readable summary.

Usage:
    python report_generator.py --mission-dir logs/missions/mission_20260226_060000
    python report_generator.py --mission-dir logs/missions/latest
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_mission_result(mission_dir: str) -> dict:
    result_path = Path(mission_dir) / "mission_result.json"
    if not result_path.exists():
        raise FileNotFoundError(f"No mission_result.json found in {mission_dir}")
    with open(result_path) as f:
        return json.load(f)


def generate_markdown_report(result: dict) -> str:
    lines = [
        f"# Mission Report: {result['mission_id']}",
        "",
        f"**Status:** {result['status']}",
        f"**Start:** {result['start_time']}",
        f"**End:** {result.get('end_time', 'N/A')}",
        f"**Checkpoints:** {result['checkpoints_completed']}/{result['checkpoints_total']}",
        f"**Images Captured:** {result['images_captured']}",
        "",
        "---",
        "",
        "## Alerts",
        "",
    ]

    if result.get("alerts"):
        lines.append("| Time | Severity | Checkpoint | Message |")
        lines.append("| ---- | -------- | ---------- | ------- |")
        for alert in result["alerts"]:
            lines.append(
                f"| {alert.get('timestamp', 'N/A')} "
                f"| {alert.get('severity', 'N/A')} "
                f"| {alert.get('checkpoint', 'N/A')} "
                f"| {alert.get('message', '')} |"
            )
    else:
        lines.append("No alerts triggered during this mission.")

    lines.extend([
        "",
        "---",
        "",
        "## Summary",
        "",
    ])

    total = result["checkpoints_total"]
    passed = result["checkpoints_completed"]
    rate = (passed / total * 100) if total > 0 else 0

    lines.append(f"- **Success Rate:** {rate:.0f}% ({passed}/{total} checkpoints passed)")
    lines.append(f"- **Alerts Fired:** {len(result.get('alerts', []))}")

    if result["status"] == "SUCCESS":
        lines.append("- **Outcome:** Mission completed successfully with no critical issues.")
    elif "ABORTED" in result["status"]:
        lines.append(f"- **Outcome:** Mission aborted — {result['status']}")
    else:
        lines.append(f"- **Outcome:** {result['status']}")

    lines.extend([
        "",
        "---",
        "",
        f"*Report generated at {datetime.utcnow().isoformat()} UTC*",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Mission Report Generator")
    parser.add_argument("--mission-dir", required=True, help="Path to mission output directory")
    args = parser.parse_args()

    result = load_mission_result(args.mission_dir)
    report = generate_markdown_report(result)

    output_path = Path(args.mission_dir) / "report.md"
    with open(output_path, "w") as f:
        f.write(report)
    logger.info("Report written to %s", output_path)

    print(report)


if __name__ == "__main__":
    main()
