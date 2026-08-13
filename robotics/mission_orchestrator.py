"""
Mission Orchestrator
---------------------
Schedules and executes inspection missions on a configurable checkpoint
sequence. Monitors robot health throughout the mission and triggers
alerts on anomalies.

Usage:
    python mission_orchestrator.py --config inspection_config.yaml
    python mission_orchestrator.py --config inspection_config.yaml --dry-run
"""

import argparse
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from spot_client import SpotClient, RobotStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class MissionResult:
    def __init__(self, mission_id: str):
        self.mission_id = mission_id
        self.start_time = datetime.utcnow().isoformat()
        self.end_time: Optional[str] = None
        self.status = "IN_PROGRESS"
        self.checkpoints: list[dict] = []
        self.alerts: list[dict] = []
        self.images: list[str] = []

    def complete(self, status: str = "SUCCESS"):
        self.end_time = datetime.utcnow().isoformat()
        self.status = status

    def to_dict(self) -> dict:
        return {
            "mission_id": self.mission_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "checkpoints_completed": len([c for c in self.checkpoints if c.get("status") == "PASS"]),
            "checkpoints_total": len(self.checkpoints),
            "alerts": self.alerts,
            "images_captured": len(self.images),
        }


class MissionOrchestrator:
    """
    Executes a sequence of inspection checkpoints with health monitoring.

    Config structure (inspection_config.yaml):
        mission:
          name: "Facility Inspection"
          checkpoints:
            - id: "cp_01"
              name: "Entry Gate"
              actions: ["capture_image", "check_status"]
              pass_criteria:
                battery_min: 20
    """

    def __init__(self, config: dict, spot: SpotClient):
        self.config = config
        self.spot = spot
        mission_cfg = config.get("mission", {})
        self.mission_name = mission_cfg.get("name", "Unnamed Mission")
        self.checkpoints = mission_cfg.get("checkpoints", [])
        self.health_check_interval = mission_cfg.get("health_check_interval_sec", 30)

        self.output_dir = Path(config.get("output", {}).get("mission_dir", "logs/missions"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, dry_run: bool = False) -> MissionResult:
        mission_id = f"mission_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        result = MissionResult(mission_id)
        mission_dir = self.output_dir / mission_id
        mission_dir.mkdir(parents=True, exist_ok=True)

        logger.info("Starting mission: %s (%s)", self.mission_name, mission_id)
        logger.info("Checkpoints: %d", len(self.checkpoints))

        if dry_run:
            logger.info("DRY RUN — no robot commands will be sent")
            for cp in self.checkpoints:
                result.checkpoints.append({
                    "id": cp["id"],
                    "name": cp.get("name", cp["id"]),
                    "status": "DRY_RUN",
                    "actions": cp.get("actions", []),
                })
            result.complete("DRY_RUN")
            self._save_result(result, mission_dir)
            return result

        if not self.spot.connect():
            result.complete("CONNECTION_FAILED")
            self._save_result(result, mission_dir)
            return result

        try:
            for i, cp in enumerate(self.checkpoints):
                cp_id = cp["id"]
                cp_name = cp.get("name", cp_id)
                logger.info("Checkpoint %d/%d: %s", i + 1, len(self.checkpoints), cp_name)

                cp_result = self._execute_checkpoint(cp, mission_dir)
                result.checkpoints.append(cp_result)

                if cp_result.get("images"):
                    result.images.extend(cp_result["images"])

                if cp_result["status"] == "FAIL":
                    alert = {
                        "timestamp": datetime.utcnow().isoformat(),
                        "checkpoint": cp_id,
                        "message": cp_result.get("reason", "Checkpoint failed"),
                        "severity": "WARNING",
                    }
                    result.alerts.append(alert)
                    logger.warning("Checkpoint %s FAILED: %s", cp_id, alert["message"])

                # Health check between checkpoints
                status = self.spot.get_status()
                if status.is_estopped:
                    result.alerts.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "checkpoint": cp_id,
                        "message": "E-STOP triggered — aborting mission",
                        "severity": "CRITICAL",
                    })
                    result.complete("ABORTED_ESTOP")
                    break

                if status.battery_percent < 10:
                    result.alerts.append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "checkpoint": cp_id,
                        "message": f"Low battery ({status.battery_percent:.0f}%) — aborting",
                        "severity": "CRITICAL",
                    })
                    result.complete("ABORTED_LOW_BATTERY")
                    break

            if result.status == "IN_PROGRESS":
                result.complete("SUCCESS")

        except Exception as e:
            logger.error("Mission failed: %s", e)
            result.complete("ERROR")
            result.alerts.append({
                "timestamp": datetime.utcnow().isoformat(),
                "message": str(e),
                "severity": "CRITICAL",
            })
        finally:
            self.spot.disconnect()

        self._save_result(result, mission_dir)
        logger.info("Mission %s completed: %s", mission_id, result.status)
        return result

    def _execute_checkpoint(self, checkpoint: dict, mission_dir: Path) -> dict:
        cp_result = {
            "id": checkpoint["id"],
            "name": checkpoint.get("name", checkpoint["id"]),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "PASS",
            "images": [],
        }

        actions = checkpoint.get("actions", [])
        criteria = checkpoint.get("pass_criteria", {})

        for action in actions:
            if action == "capture_image":
                img_path = self.spot.capture_image(save_dir=str(mission_dir / "images"))
                if img_path:
                    cp_result["images"].append(img_path)

            elif action == "check_status":
                status = self.spot.get_status()
                cp_result["robot_status"] = {
                    "battery": status.battery_percent,
                    "powered": status.is_powered_on,
                    "faults": status.faults,
                }

                if criteria.get("battery_min") and status.battery_percent < criteria["battery_min"]:
                    cp_result["status"] = "FAIL"
                    cp_result["reason"] = f"Battery {status.battery_percent:.0f}% below minimum {criteria['battery_min']}%"

                if status.faults:
                    cp_result["status"] = "FAIL"
                    cp_result["reason"] = f"Active faults: {', '.join(status.faults)}"

        return cp_result

    def _save_result(self, result: MissionResult, mission_dir: Path):
        output = mission_dir / "mission_result.json"
        with open(output, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        logger.info("Mission result saved: %s", output)


def main():
    parser = argparse.ArgumentParser(description="Mission Orchestrator")
    parser.add_argument("--config", default="inspection_config.yaml", help="Mission config")
    parser.add_argument("--dry-run", action="store_true", help="Preview without robot commands")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    spot = SpotClient()
    orchestrator = MissionOrchestrator(config, spot)
    result = orchestrator.run(dry_run=args.dry_run)

    print(json.dumps(result.to_dict(), indent=2))


if __name__ == "__main__":
    main()
