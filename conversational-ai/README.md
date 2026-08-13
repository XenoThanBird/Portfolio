# Conversational AI

End-to-end conversational AI engineering: intent routing, prompt design,
NLP analytics, and speech-recognition optimization. These four modules
cover the full lifecycle of a production voice/chat channel — from the
utterance hitting the ASR engine, through intent classification and
routing, to the prompts driving LLM-backed responses, and the analytics
that measure all of it.

## Modules

### [`ivr-routing/`](ivr-routing/) — Conversational IVR Routing

Confidence-based intent routing with LLM fallback. A routing engine
(`router_logic.py`) classifies utterances against a task map, escalating
low-confidence hits to an LLM and, below threshold, to a live agent.
Includes a batch evaluator for measuring routing accuracy against CSV
test sets and a cosine-similarity utterance clustering example.

### [`prompt-engineering/`](prompt-engineering/) — Prompt Engineering & Function Calling

Enterprise GPT-4o prompt sets for billing and support bots, a function
calling schema defining six OpenAI tools, few-shot examples, and a
Jupyter test runner for prompt validation against a CSV test set.

### [`nlp-tools/`](nlp-tools/) — NLP Analysis Tools

Two Streamlit apps — a cosine-similarity scorer for semantic utterance
comparison and an LLM performance analytics dashboard (confidence
distributions, fallback rates, misclassified intent pairs) — plus an
address-normalization training pipeline built on libpostal.

### [`asr-lab/`](asr-lab/) — ASR Optimization Lab

Automatic Speech Recognition configuration testing for IVR systems.
Batch-tests ASR configs against background-noise scenarios, calculates
sensitivity thresholds via RMS analysis, and compares configurations
across Azure Speech, Deepgram, and Speechmatics engines. Streamlit
testing dashboard and Docker support included; has its own
`requirements.txt`.

## Quickstart

```bash
# From the repository root, with requirements installed:
streamlit run conversational-ai/nlp-tools/streamlit_cosine_tool.py

# Batch-evaluate the IVR router:
python conversational-ai/ivr-routing/batch_evaluator.py
```

All test data in these modules is synthetic.
