"""
AI Value Assessment Engine.
Adapted from the AI Value Assessment Framework for enterprise AI initiative scoring.
Provides ROI calculation, risk scoring, value scoring, use case prioritization, and roadmap generation.
"""

from typing import Dict, List


class ValueEngine:
    """Enterprise AI value assessment calculator."""

    def __init__(self, config: Dict | None = None) -> None:
        from app.config import load_scoring_config

        cfg = config or load_scoring_config()

        self.value_weights = cfg.get("value_weights", {
            "financial_impact": 0.30,
            "operational_excellence": 0.20,
            "strategic_value": 0.15,
            "risk_mitigation": 0.15,
            "customer_impact": 0.10,
            "innovation_index": 0.10,
        })

        self.readiness_weights = cfg.get("readiness_weights", {
            "data_maturity": 0.35,
            "organizational_readiness": 0.35,
            "technical_capability": 0.30,
        })

        self.action_matrix = {
            (90, 100): {"classification": "Transformational", "action": "Full deployment", "investment": "$50M+"},
            (75, 89): {"classification": "Strategic", "action": "Phased rollout", "investment": "$20-50M"},
            (60, 74): {"classification": "Tactical", "action": "Pilot program", "investment": "$5-20M"},
            (45, 59): {"classification": "Experimental", "action": "Limited POC", "investment": "$1-5M"},
            (0, 44): {"classification": "Monitor", "action": "Research only", "investment": "<$1M"},
        }

    def calculate_value_score(
        self,
        components: Dict[str, float],
        readiness: Dict[str, float],
    ) -> Dict:
        """
        Calculate comprehensive enterprise AI value score.

        Args:
            components: Dict of component scores (0-100)
            readiness: Dict of readiness scores (0-1)

        Returns:
            Dict with base_score, readiness_multiplier, final_score, classification, etc.
        """
        base_score = sum(
            components.get(comp, 0) * self.value_weights.get(comp, 0)
            for comp in self.value_weights
        )

        readiness_multiplier = sum(
            readiness.get(factor, 0) * self.readiness_weights.get(factor, 0)
            for factor in self.readiness_weights
        )

        final_score = base_score * readiness_multiplier

        recommendation = {"classification": "Monitor", "action": "Research only", "investment": "<$1M"}
        for (low, high), action_info in self.action_matrix.items():
            if low <= final_score <= high:
                recommendation = action_info
                break

        return {
            "base_score": round(base_score, 1),
            "readiness_multiplier": round(readiness_multiplier, 2),
            "final_score": round(final_score, 1),
            "classification": recommendation["classification"],
            "recommended_action": recommendation["action"],
            "investment_range": recommendation["investment"],
        }

    def calculate_roi(
        self,
        benefits: float,
        costs: float,
        years: int = 3,
        discount_rate: float = 0.10,
    ) -> Dict[str, float]:
        """
        Calculate comprehensive ROI metrics.

        Args:
            benefits: Total expected benefits ($M)
            costs: Total implementation costs ($M)
            years: Time horizon for NPV calculation
            discount_rate: Discount rate for NPV
        """
        roi = ((benefits - costs) / costs) * 100 if costs > 0 else 0

        annual_cashflow = (benefits - costs) / years if years > 0 else 0
        npv = sum(
            annual_cashflow / ((1 + discount_rate) ** t)
            for t in range(1, years + 1)
        ) - costs

        payback = costs / (benefits / years) if benefits > 0 and years > 0 else float("inf")

        risk_factor = 0.20
        raroi = roi * (1 - risk_factor)

        return {
            "roi_percent": round(roi, 1),
            "npv_millions": round(npv, 2),
            "payback_years": round(min(payback, 99), 2),
            "risk_adjusted_roi": round(raroi, 1),
        }

    def prioritize_use_cases(self, use_cases: List[Dict]) -> List[Dict]:
        """
        Prioritize use cases based on value, complexity, and readiness.

        Args:
            use_cases: List of dicts with keys: use_case, value_potential,
                       complexity (1-5), time_months, data_readiness (1-5), risk_level (1-5)
        """
        scored = []
        for uc in use_cases:
            priority_score = (
                uc.get("value_potential", 0) * 0.35
                + (6 - uc.get("complexity", 3)) * 0.20 * 20
                + (12 - uc.get("time_months", 6)) * 0.15 * 8.33
                + uc.get("data_readiness", 3) * 0.20 * 20
                + (6 - uc.get("risk_level", 3)) * 0.10 * 20
            )

            vp = uc.get("value_potential", 0)
            cx = uc.get("complexity", 3)
            dr = uc.get("data_readiness", 3)

            if vp > 50 and cx <= 2:
                category = "Quick Win"
            elif vp > 70 and cx >= 4:
                category = "Strategic Bet"
            elif dr >= 4:
                category = "Foundation"
            else:
                category = "Standard"

            scored.append({
                **uc,
                "priority_score": round(priority_score, 1),
                "category": category,
            })

        scored.sort(key=lambda x: x["priority_score"], reverse=True)
        for i, item in enumerate(scored, 1):
            item["rank"] = i

        return scored

    def generate_roadmap(
        self,
        current_maturity: int,
        target_maturity: int,
        budget_millions: float,
    ) -> Dict:
        """Generate implementation roadmap based on maturity and budget."""
        phases = []

        # Phase 0: Assessment (always included)
        phases.append({
            "phase": "Assessment",
            "duration_months": 3,
            "focus": "Current state analysis, use case identification",
            "budget_allocation": min(2, budget_millions * 0.05),
            "key_deliverables": ["Readiness report", "Use case portfolio", "Business case"],
        })

        if current_maturity <= 2:
            phases.append({
                "phase": "Foundation",
                "duration_months": 6,
                "focus": "Data infrastructure, governance, team building",
                "budget_allocation": min(15, budget_millions * 0.30),
                "key_deliverables": ["Data platform", "Governance framework", "Core team"],
            })

        phases.append({
            "phase": "Pilot",
            "duration_months": 6,
            "focus": "3-5 high-value use cases",
            "budget_allocation": min(20, budget_millions * 0.25),
            "key_deliverables": ["POC results", "ROI validation", "Lessons learned"],
        })

        if budget_millions > 50:
            phases.append({
                "phase": "Scale",
                "duration_months": 12,
                "focus": "10-15 use cases, production deployment",
                "budget_allocation": min(40, budget_millions * 0.35),
                "key_deliverables": ["Production systems", "Process integration", "Change management"],
            })

        if target_maturity >= 4 and budget_millions > 100:
            remaining = budget_millions - sum(p["budget_allocation"] for p in phases)
            phases.append({
                "phase": "Transform",
                "duration_months": 12,
                "focus": "AI-first processes, innovation platform",
                "budget_allocation": max(0, remaining),
                "key_deliverables": ["AI-native capabilities", "Innovation ecosystem", "Cultural transformation"],
            })

        total_duration = sum(p["duration_months"] for p in phases)
        total_budget = sum(p["budget_allocation"] for p in phases)

        base_prob = 0.3 + (current_maturity * 0.15)
        budget_factor = min(1.0, budget_millions / 50)
        probability = min(0.95, base_prob * (1 + budget_factor * 0.3))

        return {
            "phases": phases,
            "total_duration_months": total_duration,
            "total_budget_millions": round(total_budget, 1),
            "maturity_progression": f"Level {current_maturity} -> Level {target_maturity}",
            "success_probability": f"{round(probability * 100)}%",
        }
