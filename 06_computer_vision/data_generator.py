"""
Synthetic Sensor Data Generator
--------------------------------
Generates realistic time-series sensor data with configurable anomaly injection.
Stores output in SQLite for use with the Anomaly Detection Pipeline.

Usage:
    python data_generator.py --sensors 5 --hours 24 --anomaly-rate 0.03
    python data_generator.py --sensors 10 --hours 168 --anomaly-rate 0.05 --db custom.db
"""

import argparse
import logging
import sqlite3
from datetime import datetime, timedelta

import numpy as np

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SENSOR_PROFILES = {
    "temperature": {"mean": 45.0, "std": 5.0, "unit": "°C"},
    "vibration": {"mean": 3.2, "std": 1.5, "unit": "mm/s"},
    "pressure": {"mean": 101.3, "std": 2.0, "unit": "kPa"},
    "humidity": {"mean": 55.0, "std": 10.0, "unit": "%"},
    "current": {"mean": 12.5, "std": 2.0, "unit": "A"},
}


def create_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            sensor_id TEXT NOT NULL,
            metric TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT,
            is_anomaly INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sensor_ts
        ON sensor_readings(sensor_id, timestamp)
    """)
    conn.commit()
    return conn


def generate_data(
    n_sensors: int,
    hours: int,
    anomaly_rate: float,
    interval_seconds: int = 60,
) -> list[dict]:
    metrics = list(SENSOR_PROFILES.keys())
    readings = []
    start = datetime.utcnow() - timedelta(hours=hours)
    n_points = (hours * 3600) // interval_seconds

    rng = np.random.default_rng(seed=42)

    for i in range(n_sensors):
        metric = metrics[i % len(metrics)]
        profile = SENSOR_PROFILES[metric]
        sensor_id = f"sensor_{i+1:03d}"

        base = rng.normal(profile["mean"], profile["std"], n_points)

        # Add diurnal pattern for realism
        t = np.linspace(0, hours / 24 * 2 * np.pi, n_points)
        base += np.sin(t) * profile["std"] * 0.3

        # Inject anomalies
        anomaly_mask = rng.random(n_points) < anomaly_rate
        anomaly_magnitude = rng.choice([-1, 1], n_points) * profile["std"] * rng.uniform(3, 6, n_points)
        base[anomaly_mask] += anomaly_magnitude[anomaly_mask]

        for j in range(n_points):
            ts = start + timedelta(seconds=j * interval_seconds)
            readings.append({
                "timestamp": ts.isoformat(),
                "sensor_id": sensor_id,
                "metric": metric,
                "value": round(float(base[j]), 3),
                "unit": profile["unit"],
                "is_anomaly": int(anomaly_mask[j]),
            })

    return readings


def main():
    parser = argparse.ArgumentParser(description="Synthetic Sensor Data Generator")
    parser.add_argument("--sensors", type=int, default=5, help="Number of sensors")
    parser.add_argument("--hours", type=int, default=24, help="Hours of data to generate")
    parser.add_argument("--anomaly-rate", type=float, default=0.03, help="Fraction of anomalous readings")
    parser.add_argument("--interval", type=int, default=60, help="Seconds between readings")
    parser.add_argument("--db", default="sensor_data.db", help="SQLite database path")
    args = parser.parse_args()

    conn = create_db(args.db)
    readings = generate_data(args.sensors, args.hours, args.anomaly_rate, args.interval)

    conn.executemany(
        "INSERT INTO sensor_readings (timestamp, sensor_id, metric, value, unit, is_anomaly) "
        "VALUES (:timestamp, :sensor_id, :metric, :value, :unit, :is_anomaly)",
        readings,
    )
    conn.commit()

    total = len(readings)
    anomalies = sum(1 for r in readings if r["is_anomaly"])
    logger.info(
        "Generated %d readings (%d anomalies, %.1f%%) for %d sensors over %d hours → %s",
        total, anomalies, anomalies / total * 100, args.sensors, args.hours, args.db,
    )
    conn.close()


if __name__ == "__main__":
    main()
