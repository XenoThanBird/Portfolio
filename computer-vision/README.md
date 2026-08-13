# Computer Vision & Anomaly Detection

Multi-modal computer vision, time-series anomaly detection, and GPU-accelerated monitoring systems for critical infrastructure.

This section contains two generic, reusable templates that demonstrate production patterns for visual monitoring and sensor-based anomaly detection — without any proprietary data or employer-specific configurations.

---

## Templates

### 1. Vision Monitoring Pipeline

A configurable YOLOv8 + BLIP-2 monitoring scaffold for real-time object detection and scene understanding.

| File | Description |
| ---- | ----------- |
| `vision_monitor.py` | Main pipeline — camera/video input, YOLOv8 detection, BLIP-2 scene description |
| `alert_pipeline.py` | Configurable alert/logging system with severity levels and cooldowns |
| `config.yaml` | Pipeline configuration (model paths, thresholds, alert rules, input sources) |
| `.env.template` | Environment variable template for API keys and paths |

**Features:**

- Webcam or video file input (no facility-specific cameras)
- YOLOv8 object detection with configurable class filtering
- BLIP-2 vision-language model for natural language scene descriptions
- Multi-level alert pipeline (INFO/WARNING/CRITICAL) with cooldown logic
- CSV and JSON logging for downstream analytics
- Grafana-compatible metric output

**Run:**

```bash
pip install ultralytics transformers torch opencv-python pillow
python vision_monitor.py --source webcam
python vision_monitor.py --source samples/demo_video.mp4
```

---

### 2. Anomaly Detection Pipeline

A generic time-series anomaly detection system for sensor data, with configurable detection strategies and dashboard-ready output.

| File | Description |
| ---- | ----------- |
| `anomaly_detector.py` | Detection engine — threshold, z-score, and isolation forest strategies |
| `data_generator.py` | Synthetic sensor data generator for testing and demos |
| `metrics_exporter.py` | Grafana-compatible metric exporter (Prometheus format) |
| `config.yaml` | Detection thresholds, model parameters, data source configuration |

**Features:**

- SQLite storage for time-series sensor readings
- Three detection strategies: static threshold, z-score, isolation forest
- Synthetic data generator with configurable anomaly injection
- Prometheus-format metric output for Grafana dashboards
- Batch and streaming detection modes
- Alert history with severity classification

**Run:**

```bash
pip install pandas numpy scikit-learn
python data_generator.py --sensors 5 --hours 24 --anomaly-rate 0.03
python anomaly_detector.py --strategy zscore --threshold 2.5
python metrics_exporter.py --port 9090
```

---

## Tech Stack

`Python` `YOLOv8` `BLIP-2` `OpenCV` `Transformers` `scikit-learn` `SQLite` `Prometheus` `Grafana`
