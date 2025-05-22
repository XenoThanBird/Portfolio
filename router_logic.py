#Router Logic file loads your router_taskmap.json
#Applies threshold logic based on confidence score
#Routes or falls back to the Agent Bot
#Includes a test runner with sample intent inputs

import json

# Load router task map
with open('router_taskmap.json', 'r') as f:
    task_map = json.load(f)

def route_intent(intent_label, confidence_score):
    if intent_label not in task_map:
        return {
            "status": "fallback",
            "reason": "Unknown intent",
            "route": task_map["Unknown"]
        }

    route_info = task_map[intent_label]
    if confidence_score >= route_info["threshold"]:
        return {
            "status": "routed",
            "bot_name": route_info["bot_name"],
            "task_endpoint": route_info["task_endpoint"],
            "confidence_score": confidence_score
        }
    else:
        return {
            "status": "fallback",
            "reason": "Confidence below threshold",
            "route": task_map["AgentRequest"]
        }

# Simulate a few test examples
if __name__ == "__main__":
    test_cases = [
        {"intent": "CableBalanceInquiry", "confidence": 0.92},
        {"intent": "MobilePaymentSubmission", "confidence": 0.79},
        {"intent": "CableOutageReport", "confidence": 0.65},
        {"intent": "Unknown", "confidence": 0.42},
        {"intent": "RouterRebootRequest", "confidence": 0.70}
    ]

    for test in test_cases:
        result = route_intent(test["intent"], test["confidence"])
        print(f"Input: {test}\nResult: {json.dumps(result, indent=2)}\n")
