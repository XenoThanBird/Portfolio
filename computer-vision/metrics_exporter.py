"""
Metrics Exporter
----------------
Exports anomaly detection and sensor metrics in Prometheus format
for Grafana dashboard integration.

Usage:
    python metrics_exporter.py --port 9090
    python metrics_exporter.py --port 9090 --db sensor_data.db

Then configure Grafana to scrape http://localhost:9090/metrics
"""

import argparse
import logging
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler

import yaml

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def collect_metrics(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    lines = []

    # Total readings per sensor
    lines.append("# HELP sensor_readings_total Total sensor readings by sensor")
    lines.append("# TYPE sensor_readings_total counter")
    rows = conn.execute(
        "SELECT sensor_id, COUNT(*) FROM sensor_readings GROUP BY sensor_id"
    ).fetchall()
    for sensor_id, count in rows:
        lines.append(f'sensor_readings_total{{sensor_id="{sensor_id}"}} {count}')

    # Latest value per sensor
    lines.append("# HELP sensor_latest_value Most recent sensor reading")
    lines.append("# TYPE sensor_latest_value gauge")
    rows = conn.execute("""
        SELECT sensor_id, metric, value FROM sensor_readings
        WHERE id IN (SELECT MAX(id) FROM sensor_readings GROUP BY sensor_id)
    """).fetchall()
    for sensor_id, metric, value in rows:
        lines.append(f'sensor_latest_value{{sensor_id="{sensor_id}",metric="{metric}"}} {value}')

    # Anomaly counts per sensor
    lines.append("# HELP sensor_anomalies_total Total anomalies detected by sensor")
    lines.append("# TYPE sensor_anomalies_total counter")
    rows = conn.execute(
        "SELECT sensor_id, COUNT(*) FROM sensor_readings WHERE is_anomaly = 1 GROUP BY sensor_id"
    ).fetchall()
    for sensor_id, count in rows:
        lines.append(f'sensor_anomalies_total{{sensor_id="{sensor_id}"}} {count}')

    # Anomaly rate
    total = conn.execute("SELECT COUNT(*) FROM sensor_readings").fetchone()[0]
    anomalies = conn.execute("SELECT COUNT(*) FROM sensor_readings WHERE is_anomaly = 1").fetchone()[0]
    rate = anomalies / total if total > 0 else 0
    lines.append("# HELP sensor_anomaly_rate Overall anomaly rate")
    lines.append("# TYPE sensor_anomaly_rate gauge")
    lines.append(f"sensor_anomaly_rate {rate:.6f}")

    conn.close()
    return "\n".join(lines) + "\n"


class MetricsHandler(BaseHTTPRequestHandler):
    db_path = "sensor_data.db"

    def do_GET(self):
        if self.path == "/metrics":
            body = collect_metrics(self.db_path)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.end_headers()
            self.wfile.write(body.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return  # Suppress default HTTP logging


def main():
    parser = argparse.ArgumentParser(description="Prometheus Metrics Exporter")
    parser.add_argument("--port", type=int, default=9090, help="HTTP port")
    parser.add_argument("--db", default="sensor_data.db", help="SQLite database path")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()

    MetricsHandler.db_path = args.db
    server = HTTPServer(("0.0.0.0", args.port), MetricsHandler)
    logger.info("Serving Prometheus metrics on http://localhost:%d/metrics", args.port)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Exporter stopped")
        server.server_close()


if __name__ == "__main__":
    main()
