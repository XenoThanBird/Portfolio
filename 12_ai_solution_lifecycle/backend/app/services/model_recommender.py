"""
AI model recommendation engine.
Suggests appropriate models based on use case descriptions and catalog context.
"""

import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.model_catalog import AIModel
from app.services.llm_provider import LLMProvider


async def recommend_models(
    use_case_description: str,
    db: Session,
    llm: LLMProvider,
    project_id: Optional[str] = None,
) -> list[dict]:
    """
    Recommend AI models for a given use case.

    Args:
        use_case_description: Natural language description of the use case
        db: Database session
        llm: LLM provider instance
        project_id: Optional project context

    Returns:
        List of recommendations with model_id, model_name, confidence, rationale
    """
    # Load all models from catalog
    models = db.query(AIModel).all()

    if not models:
        return [{
            "model_id": None,
            "model_name": "No models in catalog",
            "confidence": 0,
            "rationale": "Add models to the catalog first.",
        }]

    # Build catalog context for the LLM
    catalog_text = "Available AI Models:\n\n"
    for m in models:
        catalog_text += f"- **{m.name}** ({m.provider or 'unknown'}, {m.model_type or 'general'})\n"
        if m.description:
            catalog_text += f"  Description: {m.description}\n"
        if m.capabilities:
            catalog_text += f"  Capabilities: {', '.join(m.capabilities)}\n"
        if m.strengths:
            catalog_text += f"  Strengths: {', '.join(m.strengths)}\n"
        if m.limitations:
            catalog_text += f"  Limitations: {', '.join(m.limitations)}\n"
        if m.cost_per_1k_tokens is not None:
            catalog_text += f"  Cost: ${m.cost_per_1k_tokens}/1K tokens\n"
        catalog_text += "\n"

    system_prompt = """You are an AI solutions architect. Given a catalog of available AI models and a use case description, recommend the top 3 most suitable models. For each recommendation, provide:
1. The model name (exactly as listed in the catalog)
2. A confidence score (0.0 to 1.0)
3. A brief rationale explaining why this model fits

Respond in JSON format:
[{"model_name": "...", "confidence": 0.95, "rationale": "..."}]"""

    prompt = f"""{catalog_text}

Use Case: {use_case_description}

Recommend the top 3 models for this use case. Respond with a JSON array only."""

    response = await llm.generate(
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=1000,
        temperature=0.3,
    )

    # Parse LLM response
    recommendations = _parse_recommendations(response.content, models)
    return recommendations


def _parse_recommendations(content: str, models: list) -> list[dict]:
    """Parse LLM recommendation response into structured format."""
    model_lookup = {m.name.lower(): m for m in models}

    try:
        # Try to extract JSON from response
        start = content.find("[")
        end = content.rfind("]") + 1
        if start >= 0 and end > start:
            parsed = json.loads(content[start:end])
            results = []
            for rec in parsed[:3]:
                model_name = rec.get("model_name", "")
                model = model_lookup.get(model_name.lower())
                results.append({
                    "model_id": model.id if model else None,
                    "model_name": model_name,
                    "confidence": min(1.0, max(0.0, float(rec.get("confidence", 0.5)))),
                    "rationale": rec.get("rationale", ""),
                })
            return results
    except (json.JSONDecodeError, ValueError, KeyError):
        pass

    # Fallback: return first 3 models from catalog
    return [
        {
            "model_id": m.id,
            "model_name": m.name,
            "confidence": round(0.9 - (i * 0.1), 2),
            "rationale": f"Recommended based on {m.model_type or 'general'} capabilities.",
        }
        for i, m in enumerate(models[:3])
    ]
