"""
Anomaly Detection Pipeline
---------------------------
Generic time-series anomaly detection engine with configurable strategies:
  - Static threshold: hard min/max bounds per sensor
  - Z-score: statistical deviation from rolling mean
  - Isolation Forest: unsupervised ML-based outlier detection

Usage:
    python anomaly_detector.py --strategy zscore --threshold 2.5
    python anomaly_detector.py --strategy isolation_forest
    python anomaly_detector.py --strategy threshold
"""

import argparse
import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


class AnomalyDetector:
    """Multi-strategy anomaly detection for time-series sensor data."""

    def __init__(self, config: dict):
        ad_cfg = config.get("anomaly_detection", {})
        self.strategy = ad_cfg.get("strategy", "zscore")
        self.zscore_threshold = ad_cfg.get("zscore_threshold", 2.5)
        self.static_thresholds = ad_cfg.get("static_thresholds", {})
        self.window_size = ad_cfg.get("window_size", 60)
        self.iso_forest_cfg = ad_cfg.get("isolation_forest", {})

        db_path = config.get("storage", {}).get("database", "sensor_data.db")
        self.conn = sqlite3.connect(db_path)
        self._iso_models: dict = {}

        log_dir = Path(config.get("logging", {}).get("output_dir", "logs"))
        log_dir.mkdir(parents=True, exist_ok=True)
        self.anomaly_log = log_dir / "anomalies.jsonl"

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.strategy == "threshold":
            return self._detect_threshold(df)
        elif self.strategy == "zscore":
            return self._detect_zscore(df)
        elif self.strategy == "isolation_forest":
            return self._detect_isolation_forest(df)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}")

    def _detect_threshold(self, df: pd.DataFrame) -> pd.DataFrame:
        anomalies = []
        for _, row in df.iterrows():
            sensor = row["sensor_id"]
            value = row["value"]
            bounds = self.static_thresholds.get(row.get("metric", ""), {})
            lo, hi = bounds.get("min", float("-inf")), bounds.get("max", float("inf"))
            if value < lo or value > hi:
                anomalies.append({
                    **row.to_dict(),
                    "anomaly": True,
                    "reason": f"Out of bounds [{lo}, {hi}]",
                    "severity": "CRITICAL" if abs(value - (lo + hi) / 2) > (hi - lo) else "WARNING",
                })
        return pd.DataFrame(anomalies)

    def _detect_zscore(self, df: pd.DataFrame) -> pd.DataFrame:
        anomalies = []
        for sensor_id, group in df.groupby("sensor_id"):
            values = group["value"].values
            if len(values) < self.window_size:
                rolling_mean = np.mean(values)
                rolling_std = np.std(values) or 1e-6
            else:
                rolling_mean = np.mean(values[-self.window_size:])
                rolling_std = np.std(values[-self.window_size:]) or 1e-6

            for _, row in group.iterrows():
                z = abs((row["value"] - rolling_mean) / rolling_std)
                if z > self.zscore_threshold:
                    anomalies.append({
                        **row.to_dict(),
                        "anomaly": True,
                        "z_score": round(z, 3),
                        "reason": f"Z-score {z:.2f} > {self.zscore_threshold}",
                        "severity": "CRITICAL" if z > self.zscore_threshold * 1.5 else "WARNING",
                    })
        return pd.DataFrame(anomalies)

    def _detect_isolation_forest(self, df: pd.DataFrame) -> pd.DataFrame:
        from sklearn.ensemble import IsolationForest

        anomalies = []
        for sensor_id, group in df.groupby("sensor_id"):
            values = group[["value"]].values
            if len(values) < 10:
                continue

            if sensor_id not in self._iso_models:
                model = IsolationForest(
                    contamination=self.iso_forest_cfg.get("contamination", 0.03),
                    n_estimators=self.iso_forest_cfg.get("n_estimators", 100),
                    random_state=self.iso_forest_cfg.get("random_state", 42),
                )
                model.fit(values)
                self._iso_models[sensor_id] = model

            predictions = self._iso_models[sensor_id].predict(values)
            scores = self._iso_models[sensor_id].decision_function(values)

            for i, (pred, score) in enumerate(zip(predictions, scores)):
                if pred == -1:
                    row = group.iloc[i]
                    anomalies.append({
                        **row.to_dict(),
                        "anomaly": True,
                        "isolation_score": round(float(score), 4),
                        "reason": f"Isolation Forest outlier (score: {score:.4f})",
                        "severity": "CRITICAL" if score < -0.3 else "WARNING",
                    })
        return pd.DataFrame(anomalies)

    def log_anomalies(self, anomalies: pd.DataFrame):
        if anomalies.empty:
            return
        with open(self.anomaly_log, "a") as f:
            for _, row in anomalies.iterrows():
                record = {
                    "detected_at": datetime.utcnow().isoformat(),
                    **{k: v for k, v in row.to_dict().items() if pd.notna(v)},
                }
                f.write(json.dumps(record, default=str) + "\n")
        logger.info("Logged %d anomalies to %s", len(anomalies), self.anomaly_log)

    def run_batch(self, table: str = "sensor_readings") -> pd.DataFrame:
        df = pd.read_sql(f"SELECT * FROM {table} ORDER BY timestamp", self.conn)
        if df.empty:
            logger.info("No data found in %s", table)
            return pd.DataFrame()

        logger.info("Analyzing %d readings with strategy: %s", len(df), self.strategy)
        anomalies = self.detect(df)
        logger.info("Found %d anomalies", len(anomalies))
        self.log_anomalies(anomalies)
        return anomalies


def main():
    parser = argparse.ArgumentParser(description="Anomaly Detection Pipeline")
    parser.add_argument("--strategy", choices=["threshold", "zscore", "isolation_forest"])
    parser.add_argument("--threshold", type=float, help="Z-score threshold override")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.strategy:
        config.setdefault("anomaly_detection", {})["strategy"] = args.strategy
    if args.threshold:
        config.setdefault("anomaly_detection", {})["zscore_threshold"] = args.threshold

    detector = AnomalyDetector(config)
    anomalies = detector.run_batch()

    if not anomalies.empty:
        print(f"\n{'='*60}")
        print(f"  ANOMALY REPORT — {len(anomalies)} anomalies detected")
        print(f"{'='*60}")
        print(anomalies[["timestamp", "sensor_id", "value", "severity", "reason"]].to_string(index=False))


if __name__ == "__main__":
    main()
