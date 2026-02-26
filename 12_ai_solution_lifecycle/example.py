"""
AI Solution Lifecycle Platform — CLI Demo

Demonstrates backend capabilities without running the full server:
  1. Creates a project
  2. Runs the value assessment engine
  3. Calculates ROI
  4. Generates a roadmap
  5. Evaluates risks
  6. Prioritizes use cases

Usage:
    cd 12_ai_solution_lifecycle
    python example.py
"""

import sys
from pathlib import Path

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.services.value_engine import ValueEngine


def main():
    engine = ValueEngine()

    print("=" * 70)
    print("  AI Solution Lifecycle Platform — CLI Demo")
    print("=" * 70)

    # ── 1. Value Assessment ─────────────────────────────────────────────
    print("\n1. VALUE ASSESSMENT")
    print("-" * 50)

    components = {
        "financial_impact": 85,
        "operational_excellence": 78,
        "strategic_value": 72,
        "risk_mitigation": 65,
        "customer_impact": 90,
        "innovation_index": 70,
    }
    readiness = {
        "data_maturity": 0.75,
        "organizational_readiness": 0.60,
        "technical_capability": 0.85,
    }

    score = engine.calculate_value_score(components, readiness)

    print(f"  Base Score:          {score['base_score']}")
    print(f"  Readiness Multiplier:{score['readiness_multiplier']}")
    print(f"  Final Score:         {score['final_score']}")
    print(f"  Classification:      {score['classification']}")
    print(f"  Recommended Action:  {score['recommended_action']}")
    print(f"  Investment Range:    {score['investment_range']}")

    # ── 2. ROI Calculation ──────────────────────────────────────────────
    print("\n2. ROI CALCULATION")
    print("-" * 50)

    roi = engine.calculate_roi(
        benefits=6.5,
        costs=3.2,
        years=4,
        discount_rate=0.10,
    )

    print(f"  Benefits / Costs:    $6.5M / $3.2M over 4 years")
    print(f"  ROI:                 {roi['roi_percent']}%")
    print(f"  NPV:                 ${roi['npv_millions']}M")
    print(f"  Payback Period:      {roi['payback_years']} years")
    print(f"  Risk-Adjusted ROI:   {roi['risk_adjusted_roi']}%")

    # ── 3. Roadmap Generation ───────────────────────────────────────────
    print("\n3. IMPLEMENTATION ROADMAP")
    print("-" * 50)

    roadmap = engine.generate_roadmap(
        current_maturity=2,
        target_maturity=4,
        budget_millions=5.0,
    )

    print(f"  Maturity: {roadmap['maturity_progression']}")
    print(f"  Total Duration: {roadmap['total_duration_months']} months")
    print(f"  Total Budget: ${roadmap['total_budget_millions']}M")
    print(f"  Success Probability: {roadmap['success_probability']}")
    print()
    for i, phase in enumerate(roadmap["phases"], 1):
        print(f"  Phase {i}: {phase['phase']} ({phase['duration_months']} months)")
        print(f"    Focus: {phase['focus']}")
        print(f"    Budget: ${phase['budget_allocation']}M")
        if phase.get("key_deliverables"):
            print(f"    Deliverables: {', '.join(phase['key_deliverables'])}")
        print()

    # ── 4. Use Case Prioritization ──────────────────────────────────────
    print("4. USE CASE PRIORITIZATION")
    print("-" * 50)

    use_cases = [
        {
            "use_case": "Customer Churn Prediction",
            "value_potential": 85,
            "complexity": 2,
            "time_months": 4,
            "data_readiness": 4,
            "risk_level": 2,
        },
        {
            "use_case": "Automated Report Generation",
            "value_potential": 60,
            "complexity": 1,
            "time_months": 2,
            "data_readiness": 5,
            "risk_level": 1,
        },
        {
            "use_case": "Real-Time Fraud Detection",
            "value_potential": 95,
            "complexity": 5,
            "time_months": 10,
            "data_readiness": 2,
            "risk_level": 4,
        },
        {
            "use_case": "Employee Sentiment Analysis",
            "value_potential": 40,
            "complexity": 2,
            "time_months": 3,
            "data_readiness": 3,
            "risk_level": 2,
        },
    ]

    results = engine.prioritize_use_cases(use_cases)

    for item in results:
        print(f"  #{item['rank']} [{item['category']}] {item['use_case']}")
        print(f"    Score: {item['priority_score']} | Value: {item['value_potential']} | Complexity: {item['complexity']}")
        print()

    print("=" * 70)
    print("  Demo complete. Start the full platform with:")
    print("    docker-compose up        (all services)")
    print("    cd backend && uvicorn app.main:app --reload  (backend only)")
    print("    cd frontend && npm run dev                   (frontend only)")
    print("=" * 70)


if __name__ == "__main__":
    main()
