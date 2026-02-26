# ASR Lab — Automatic Speech Recognition Optimization Toolkit

Automatic Speech Recognition (ASR) configuration testing and optimization lab for IVR systems and voice assistants, with support for Kore.ai, Azure Speech, Deepgram, and Speechmatics integrations.

---

## Problem Statement

After migrating from Nuance Krypton to Azure Speech (via UniMRCP) for ASR inside a Kore.ai-based IVR, Azure Speech Recognition exhibited hypersensitivity — hearing "background noise" and causing immediate "No Match" failures even with all prompts set to non-barge-in (non-bargeable).

Traditional ASR testing often lacks structured simulation environments, leading to:

- Overly aggressive No Match behaviors
- False positives due to background noise
- Expensive manual QA cycles

---

## What This Lab Does

- Batch-tests ASR configurations against multiple real-world background noise scenarios
- Fine-tunes speech sensitivity thresholds to optimize detection vs. background resilience
- Streamlines configuration management with YAML/JSON converters
- Provides visualization and manual testing through a Streamlit dashboard
- Supports full containerization with Docker

---

## Components

| Component | File | Description |
| :--- | :--- | :--- |
| Batch Tester | [`batch_asr_tester.py`](batch_asr_tester.py) | Tests multiple ASR configs against diverse background noise scenarios |
| Sensitivity Optimizer | [`sensitivity_optimizer.py`](sensitivity_optimizer.py) | Calculates optimal ASR sensitivity thresholds via RMS analysis |
| GUI Dashboard | [`asr_config_tester_app.py`](asr_config_tester_app.py) | Drag-and-drop testing of configs and audio samples |
| YAML/JSON Converter | [`convert_yaml_json.py`](convert_yaml_json.py) | Simplifies deployment vs. version control workflows |
| Audio Simulator | [`simulated_audio_tester.py`](simulated_audio_tester.py) | Generates synthetic noise + utterance signals and visualizes them |
| Config Comparator | [`cosine_config_comparison.py`](cosine_config_comparison.py) | Compares ASR config vectors via cosine similarity |
| Dockerfile | [`Dockerfile`](Dockerfile) | Containerizes the lab for cloud/server deployment |

## Configuration Files

| File | Description |
| :--- | :--- |
| [`configs/sample_deepgram_config.yaml`](configs/sample_deepgram_config.yaml) | Deepgram phonecall model — low sensitivity, no barge-in |
| [`configs/sample_azure_default_config.yaml`](configs/sample_azure_default_config.yaml) | Azure Speech defaults — high sensitivity (problematic baseline) |
| [`configs/sample_speechmatics_default_config.yaml`](configs/sample_speechmatics_default_config.yaml) | Speechmatics with moderate VAD sensitivity |
| [`asr_tuning_profile.yaml`](asr_tuning_profile.yaml) | Optimized Deepgram tuning profile |
| [`voice_gateway_config_profile.json`](voice_gateway_config_profile.json) | Voice gateway JSON config |
| [`example_corrected_websocket.json`](example_corrected_websocket.json) | Corrected WebSocket config example |

## Reference Documentation

| File | Description |
| :--- | :--- |
| [`gateway_config_notes.md`](gateway_config_notes.md) | Parameter-by-parameter tuning notes |
| [`sample_output.md`](sample_output.md) | Sample cosine comparison output with interpretation |
| [`cosine_similarity_pseudocode.py`](cosine_similarity_pseudocode.py) | Pseudocode for similarity scoring approach |

---

## Key Technologies

- Python 3.11
- Streamlit (GUI Dashboard)
- PyYAML, Pandas, NumPy, Pydub, Matplotlib
- scikit-learn (cosine similarity analysis)
- Docker for cloud containerization
- Deepgram, Azure Speech, Speechmatics ASR engines

---

## Usage

```bash
# Set up directories
mkdir configs backgrounds outputs

# Place YAML configs in configs/ and WAV files in backgrounds/

# Run batch testing
python batch_asr_tester.py

# Run sensitivity optimizer
python sensitivity_optimizer.py

# Launch Streamlit dashboard
streamlit run asr_config_tester_app.py

# Convert configs between YAML and JSON
python convert_yaml_json.py

# Generate simulated audio for testing
python simulated_audio_tester.py
```

### Docker

```bash
docker build -t asr-lab .
docker run -p 8501:8501 asr-lab
```

---

## Prebuilt Noise Scenarios

The lab supports testing against these background environments:

- Airport noise (white noise + loud announcements)
- Office noise (typing + light chatter)
- Street noise (traffic + honks)
- Restaurant noise (dishes + conversations)
- Crowd noise (mall chatter/murmur)

Use [`simulated_audio_tester.py`](simulated_audio_tester.py) to generate synthetic test audio, or supply your own WAV files in the `backgrounds/` directory.
