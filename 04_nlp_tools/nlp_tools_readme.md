
# NLP Tools & Dashboards

This module contains a suite of Streamlit-powered dashboards and Python pipelines designed for analyzing, training, and debugging NLP workflows in telecom IVR and enterprise LLM environments.

---

## Tools Included

### 1. `streamlit_cosine_tool.py`
Visual analyzer for comparing the semantic similarity between utterances using sentence embeddings.

- Input: List of utterances (manual or CSV)
- Output: Cosine similarity matrix + high-similarity utterance pairs
- Use Case: NLU intent de-duplication, paraphrase clustering, utterance conflict detection

**Run:**
```bash
streamlit run streamlit_cosine_tool.py
```

---

### 2. `llm_analytics_dashboard.py`
Interactive dashboard for LLM output evaluation, intent accuracy monitoring, and fallback rate analysis.

- Input: `llm_output_log.csv` (contains `intent_label`, `expected_intent`, `confidence_score`, `status`)
- Output: Histograms, pie charts, error tables
- Use Case: LLM model drift detection, zero-shot routing QA, business dashboard integration

**Run:**
```bash
streamlit run llm_analytics_dashboard.py
```

---

### 3. `address_training_pipeline.py`
End-to-end pipeline for training and testing address recognition models using `libpostal` and ML classification.

- Input: `address_samples.csv` (columns: `raw_address`, `label`)
- Output: Normalized addresses + classification accuracy
- Use Case: Enhance IVR recognition of customer-spoken addresses by region, ZIP, or routing logic

**Run:**
```bash
streamlit run address_training_pipeline.py
```

---

## Example Data

| File | Purpose |
|------|---------|
| `utterance_pairs.csv` | Sample for cosine similarity scoring |
| `llm_output_log.csv`  | Output log with intents + scores |
| `address_samples.csv` | Raw address strings labeled by region |

---

## Requirements

```bash
pip install streamlit pandas seaborn scikit-learn sentence-transformers postal
```

> Note: `libpostal` must be installed natively via `brew install libpostal` or `apt install libpostal-dev`.

---

## Ideal For

- LLM performance tuning teams
- NLU model analysts
- Telecom IVR speech/NLP engineers
- NLP feature evaluation in product pipelines

---

> “AI that isn’t tested becomes guesswork. These tools ensure insight, not assumption.”
