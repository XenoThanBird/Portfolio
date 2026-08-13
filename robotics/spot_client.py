"""
Spot SDK Client Wrapper
------------------------
Lightweight wrapper around the public Boston Dynamics Spot SDK
for common operations: authentication, navigation, image capture,
and health monitoring.

Requires: pip install bosdyn-client bosdyn-mission
Docs: https://dev.bostondynamics.com/docs/python/quickstart

This module uses only the public Spot SDK. No proprietary configurations.
"""

import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


@dataclass
class RobotStatus:
    """Snapshot of robot health and state."""
    timestamp: str = ""
    battery_percent: float = 0.0
    is_powered_on: bool = False
    is_estopped: bool = False
    uptime_seconds: float = 0.0
    current_position: dict = field(default_factory=dict)
    faults: list = field(default_factory=list)


class SpotClient:
    """
    High-level interface for Spot robot operations.

    Uses environment variables for credentials:
        SPOT_HOSTNAME - Robot IP or hostname
        SPOT_USERNAME - Authentication username
        SPOT_PASSWORD - Authentication password
    """

    def __init__(self, hostname: Optional[str] = None):
        self.hostname = hostname or os.getenv("SPOT_HOSTNAME", "192.168.80.3")
        self.username = os.getenv("SPOT_USERNAME", "user")
        self.password = os.getenv("SPOT_PASSWORD", "")
        self._sdk = None
        self._robot = None
        self._authenticated = False

    def connect(self) -> bool:
        try:
            import bosdyn.client
            from bosdyn.client import create_standard_sdk

            self._sdk = create_standard_sdk("MissionOrchestrator")
            self._robot = self._sdk.create_robot(self.hostname)
            self._robot.authenticate(self.username, self.password)
            self._robot.time_sync.wait_for_sync()
            self._authenticated = True
            logger.info("Connected to Spot at %s", self.hostname)
            return True
        except ImportError:
            logger.error(
                "bosdyn-client not installed. "
                "Install with: pip install bosdyn-client bosdyn-mission"
            )
            return False
        except Exception as e:
            logger.error("Connection failed: %s", e)
            return False

    def get_status(self) -> RobotStatus:
        if not self._authenticated:
            return RobotStatus(timestamp=datetime.utcnow().isoformat())

        try:
            state_client = self._robot.ensure_client("robot-state")
            state = state_client.get_robot_state()

            battery = state.battery_states[0] if state.battery_states else None
            return RobotStatus(
                timestamp=datetime.utcnow().isoformat(),
                battery_percent=battery.charge_percentage.value if battery else 0.0,
                is_powered_on=state.power_state.motor_power_state == 1,
                is_estopped=any(
                    s.state != 0 for s in state.estop_states
                ) if state.estop_states else False,
                uptime_seconds=state.system_state.uptime.seconds if state.system_state else 0,
                faults=[f.name for f in state.system_fault_state.faults]
                if state.system_fault_state else [],
            )
        except Exception as e:
            logger.error("Failed to get status: %s", e)
            return RobotStatus(timestamp=datetime.utcnow().isoformat())

    def capture_image(self, camera: str = "frontleft_fisheye_image", save_dir: str = "captures") -> Optional[str]:
        if not self._authenticated:
            logger.warning("Not connected — cannot capture image")
            return None

        try:
            from bosdyn.client.image import ImageClient

            image_client = self._robot.ensure_client(ImageClient.default_service_name)
            responses = image_client.get_image_from_sources([camera])

            if not responses:
                return None

            save_path = Path(save_dir)
            save_path.mkdir(parents=True, exist_ok=True)
            ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = save_path / f"{camera}_{ts}.jpg"

            with open(filename, "wb") as f:
                f.write(responses[0].shot.image.data)

            logger.info("Captured image: %s", filename)
            return str(filename)
        except Exception as e:
            logger.error("Image capture failed: %s", e)
            return None

    def power_on(self) -> bool:
        if not self._authenticated:
            return False
        try:
            from bosdyn.client.power import PowerClient
            import bosdyn.client.power as power_util

            power_client = self._robot.ensure_client(PowerClient.default_service_name)
            power_util.power_on(power_client)
            logger.info("Robot powered on")
            return True
        except Exception as e:
            logger.error("Power on failed: %s", e)
            return False

    def stand(self) -> bool:
        if not self._authenticated:
            return False
        try:
            from bosdyn.client.robot_command import RobotCommandClient, blocking_stand

            cmd_client = self._robot.ensure_client(RobotCommandClient.default_service_name)
            blocking_stand(cmd_client)
            logger.info("Robot standing")
            return True
        except Exception as e:
            logger.error("Stand failed: %s", e)
            return False

    def disconnect(self):
        if self._robot:
            try:
                self._robot.power_off(cut_immediately=False)
            except Exception:
                pass
        self._authenticated = False
        logger.info("Disconnected from Spot")
