#Batch Evaluator loads router_test_set.csv, applies the routing logic, and outputs the results to a router_batch_results.csv

import pandas as pd
import json
from pathlib import Path
from router_logic import route_intent

# Data files live next to this script, so it works from any CWD
DATA_DIR = Path(__file__).resolve().parent

# Load test set
df = pd.read_csv(DATA_DIR / 'router_test_set.csv')

# Load task map separately in case router_logic.py is executed independently
with open(DATA_DIR / 'router_taskmap.json', 'r') as f:
    task_map = json.load(f)

# Evaluate routing
results = []
for _, row in df.iterrows():
    result = route_intent(row['intent_label'], row['confidence_score'])
    results.append({
        "utterance": row['utterance'],
        "intent_label": row['intent_label'],
        "confidence_score": row['confidence_score'],
        "routing_status": result.get("status"),
        "bot_name": result.get("bot_name", result.get("route", {}).get("bot_name")),
        "task_endpoint": result.get("task_endpoint", result.get("route", {}).get("task_endpoint")),
        "reason": result.get("reason", "")
    })

# Convert results to DataFrame and save next to the input data
df_results = pd.DataFrame(results)
df_results.to_csv(DATA_DIR / "router_batch_results.csv", index=False)

print(df_results)
