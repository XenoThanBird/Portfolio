# Top-of-IVR LLM Router Design

This module demonstrates how to use a Large Language Model (LLM) as a high-precision router at the top of a Conversational IVR system. It routes 450M+ calls annually across billing, repair, account management, and authentication domains for Spectrum Residential customers.

---

## Purpose

Traditional menu-based IVRs cause friction and dropout. This router replaces rigid trees with natural language understanding powered by an LLM. It classifies intents, extracts entities, and maps user requests to downstream bots or task flows.

---

## How It Works

1. User speaks freely at the top of IVR
2. LLM evaluates the input using a prompt-trained classifier
3. System returns:
   - `intent_label` (e.g., `CableBalanceInquiry`)
   - `bot_name` or `task_endpoint`
   - `confidence_score`
4. Router logic determines fallback, reroute, or handoff

---

## Sample Task Map

```json
{
  "CableBalanceInquiry": {
    "bot": "CableBillingBot",
    "task": "BalanceInquiry",
    "threshold": 0.75
  },
  "MobileBillPayment": {
    "bot": "MobilePaymentBot",
    "task": "MakePayment",
    "threshold": 0.80
  },
  "AgentRequest": {
    "bot": "CommonBot",
    "task": "AgentTransfer",
    "threshold": 0.60
  }
}
