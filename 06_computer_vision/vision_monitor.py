"""
Vision Monitoring Pipeline
--------------------------
Generic YOLOv8 + BLIP-2 monitoring scaffold for real-time object detection
and scene understanding. Uses configurable input sources and alert thresholds.

Usage:
    python vision_monitor.py --source webcam
    python vision_monitor.py --source path/to/video.mp4
    python vision_monitor.py --source path/to/image.jpg
"""

import argparse
import csv
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
import yaml
from ultralytics import YOLO

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


class VisionMonitor:
    """Real-time object detection and scene description pipeline."""

    def __init__(self, config: dict):
        self.config = config
        det = config.get("detection", {})
        self.confidence_threshold = det.get("confidence_threshold", 0.5)
        self.target_classes = det.get("target_classes", [])
        self.frame_skip = det.get("frame_skip", 5)

        logger.info("Loading YOLOv8 model: %s", det.get("model", "yolov8n.pt"))
        self.detector = YOLO(det.get("model", "yolov8n.pt"))

        self.scene_describer = None
        if config.get("scene_description", {}).get("enabled", False):
            self._load_scene_describer(config["scene_description"])

        log_cfg = config.get("logging", {})
        self.log_dir = Path(log_cfg.get("output_dir", "logs"))
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.detections_log = self.log_dir / "detections.csv"
        if not self.detections_log.exists():
            with open(self.detections_log, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "frame", "class", "confidence",
                    "x1", "y1", "x2", "y2",
                ])

    def _load_scene_describer(self, scene_cfg: dict):
        try:
            from transformers import Blip2ForConditionalGeneration, Blip2Processor
            import torch

            model_name = scene_cfg.get("model", "Salesforce/blip2-opt-2.7b")
            logger.info("Loading BLIP-2 model: %s", model_name)
            self.scene_processor = Blip2Processor.from_pretrained(model_name)
            self.scene_model = Blip2ForConditionalGeneration.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            )
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self.scene_model.to(device)
            self.scene_device = device
            self.scene_describer = True
            logger.info("BLIP-2 loaded on %s", device)
        except ImportError:
            logger.warning("transformers/torch not installed — scene description disabled")

    def detect_objects(self, frame: np.ndarray) -> list[dict]:
        results = self.detector(frame, verbose=False)[0]
        detections = []
        for box in results.boxes:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = self.detector.names[cls_id]
            if conf < self.confidence_threshold:
                continue
            if self.target_classes and cls_name not in self.target_classes:
                continue
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            detections.append({
                "class": cls_name,
                "confidence": round(conf, 3),
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
            })
        return detections

    def describe_scene(self, frame: np.ndarray) -> Optional[str]:
        if not self.scene_describer:
            return None
        from PIL import Image
        import torch

        image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        inputs = self.scene_processor(images=image, return_tensors="pt").to(self.scene_device)
        with torch.no_grad():
            output = self.scene_model.generate(**inputs, max_new_tokens=80)
        return self.scene_processor.decode(output[0], skip_special_tokens=True)

    def log_detections(self, frame_num: int, detections: list[dict]):
        ts = datetime.utcnow().isoformat()
        with open(self.detections_log, "a", newline="") as f:
            writer = csv.writer(f)
            for det in detections:
                writer.writerow([
                    ts, frame_num, det["class"], det["confidence"],
                    *det["bbox"],
                ])

    def run(self, source: str):
        if source == "webcam":
            cap = cv2.VideoCapture(0)
        else:
            cap = cv2.VideoCapture(source)

        if not cap.isOpened():
            logger.error("Cannot open video source: %s", source)
            return

        frame_num = 0
        logger.info("Starting monitoring on source: %s", source)

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_num += 1
                if frame_num % self.frame_skip != 0:
                    continue

                detections = self.detect_objects(frame)
                if detections:
                    self.log_detections(frame_num, detections)
                    logger.info(
                        "Frame %d: %d objects — %s",
                        frame_num,
                        len(detections),
                        ", ".join(d["class"] for d in detections),
                    )

                    scene_cfg = self.config.get("scene_description", {})
                    if scene_cfg.get("on_detection", False):
                        desc = self.describe_scene(frame)
                        if desc:
                            logger.info("Scene: %s", desc)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        finally:
            cap.release()
            logger.info("Processed %d frames", frame_num)


def main():
    parser = argparse.ArgumentParser(description="Vision Monitoring Pipeline")
    parser.add_argument(
        "--source", default="webcam",
        help="Input source: 'webcam' or path to video/image file",
    )
    parser.add_argument("--config", default="config.yaml", help="Config file path")
    args = parser.parse_args()

    config = load_config(args.config)
    monitor = VisionMonitor(config)
    monitor.run(args.source)


if __name__ == "__main__":
    main()
