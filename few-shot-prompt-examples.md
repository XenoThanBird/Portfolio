# Few-Shot Prompt Examples for Function Calling

These examples are designed to teach the model how to convert natural language utterances into function calls, with extracted parameters based on context. Each section below maps to a function defined in `function-calling-schema.json`.

---

## Function: `check_bill_status`

**System Prompt**  
You are a virtual assistant that helps customers with billing inquiries by calling specific functions.

**Examples:**

**User:** I need to check my May bill.  
**Output:**
```json
{
  "function": "check_bill_status",
  "parameters": {
    "account_number": "[from_context]",
    "bill_month": "2025-05"
  }
}

**User:** Can you tell me how much I owed last month?
**Output:**
 
```json
{
  "function": "check_bill_status",
  "parameters": {
    "account_number": "[from_context]",
    "bill_month": "2025-04"
  }
}

## Function: `make_payment`

**User:** I’d like to pay $120 on my account.
**Output:**

```json
{
  "function": "make_payment",
  "parameters": {
    "account_number": "[from_context]",
    "amount": 120.00
  }
}

**User:** Please charge $90 to my Visa card.
**Output:**
```json
{
  "function": "make_payment",
  "parameters": {
    "account_number": "[from_context]",
    "amount": 90.00,
    "payment_method_id": "[visa_card_id_from_context]"
  }
}

## Function: `schedule_technician`

**User:** I want to book a technician for Friday.
**Output:**
```json
{
  "function": "schedule_technician",
  "parameters": {
    "account_number": "[from_context]",
    "preferred_date": "2025-05-23",
    "issue_type": "not specified"
  }
}

**User:** Can I get someone to come check my internet on June 3rd?
**Output:**
```json
{
  "function": "schedule_technician",
  "parameters": {
    "account_number": "[from_context]",
    "preferred_date": "2025-06-03",
    "issue_type": "internet issues"
  }
}
