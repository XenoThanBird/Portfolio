"""
Document generation service with per-doc-type system prompts.
Generates BRDs, TRDs, functional specs, design schematics, and user schematics.
"""

from app.services.llm_provider import LLMProvider, LLMResponse

SYSTEM_PROMPTS = {
    "brd": """You are an expert business analyst generating a Business Requirements Document (BRD).
Structure the document with these sections:
1. Executive Summary
2. Business Objectives (numbered list with measurable targets)
3. Scope (In Scope / Out of Scope)
4. Stakeholders (table with Role, Responsibility, Department)
5. Functional Requirements (FR-001 format)
6. Non-Functional Requirements (NFR-001 format)
7. Acceptance Criteria (bulleted checklist)
8. Timeline (phased with durations)
9. Risks and Assumptions

Use markdown formatting. Be specific and actionable. Include realistic metrics and timelines.""",

    "trd": """You are a senior solutions architect generating a Technical Requirements Document (TRD).
Structure the document with these sections:
1. Architecture Overview (technology stack, system diagram in ASCII)
2. API Design (endpoint table with Method, Path, Description)
3. Data Model (tables, relationships, key columns)
4. Security Requirements (authentication, encryption, access control)
5. Performance Requirements (latency, throughput, availability targets)
6. Integration Points (external systems, APIs, data flows)
7. Infrastructure Requirements (compute, storage, networking)
8. Deployment Strategy (CI/CD, environments, rollback)

Use markdown formatting with code blocks for diagrams and schemas.""",

    "functional": """You are a product manager generating a Functional Specification Document.
Structure the document with these sections:
1. Feature Overview
2. User Stories (As a... I want... So that...)
3. Process Flows (numbered step sequences)
4. Business Rules (BR-001 format)
5. Data Requirements (input/output specifications)
6. UI/UX Requirements (layout descriptions, interaction patterns)
7. Error Handling (error scenarios and expected behavior)
8. Testing Criteria (test scenarios per feature)

Use markdown formatting. Focus on user-facing behavior, not implementation details.""",

    "design_schematic": """You are a system designer generating a Design Schematic document.
Structure the document with these sections:
1. Component Diagram (ASCII art showing services and connections)
2. Data Flow Diagram (numbered sequence of data transformations)
3. State Diagrams (for stateful components)
4. UI Layout Description (wireframe-style descriptions)
5. Technology Decisions (table with Decision, Options Considered, Rationale)
6. Interface Contracts (API request/response formats)
7. Error Handling Strategy (error classification and routing)

Use markdown formatting with ASCII diagrams in code blocks.""",

    "user_schematic": """You are a UX designer generating a User Schematic document.
Structure the document with these sections:
1. User Personas (name, role, goals, pain points)
2. User Journey Maps (step-by-step flows per persona)
3. Screen Inventory (list of all screens/views)
4. Navigation Structure (hierarchy/sitemap)
5. Interaction Patterns (click, drag, form submission behaviors)
6. Accessibility Requirements (WCAG compliance points)
7. Responsive Breakpoints (desktop, tablet, mobile specifications)

Use markdown formatting. Focus on the human experience, not technical implementation.""",
}

DOC_TYPE_TITLES = {
    "brd": "Business Requirements Document",
    "trd": "Technical Requirements Document",
    "functional": "Functional Specification",
    "design_schematic": "Design Schematic",
    "user_schematic": "User Schematic",
}


async def generate_document(
    doc_type: str,
    user_prompt: str,
    llm: LLMProvider,
    project_name: str = "",
) -> tuple[str, str, LLMResponse]:
    """
    Generate a document using the LLM.

    Returns:
        Tuple of (title, content, llm_response)
    """
    system_prompt = SYSTEM_PROMPTS.get(doc_type, SYSTEM_PROMPTS["functional"])
    title = f"{DOC_TYPE_TITLES.get(doc_type, 'Document')}"
    if project_name:
        title += f" - {project_name}"

    enhanced_prompt = f"""Generate a {DOC_TYPE_TITLES.get(doc_type, 'document')} for the following initiative:

{user_prompt}

Produce a complete, professional document in markdown format. Include realistic details, specific metrics, and actionable items. The document should be ready for stakeholder review."""

    response = await llm.generate(
        prompt=enhanced_prompt,
        system_prompt=system_prompt,
        max_tokens=settings_max_tokens(),
        temperature=0.7,
    )

    return title, response.content, response


def settings_max_tokens() -> int:
    """Get max tokens from settings."""
    from app.config import settings
    return settings.LLM_MAX_TOKENS
