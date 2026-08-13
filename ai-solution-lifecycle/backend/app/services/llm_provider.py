"""
LLM provider abstraction using the Strategy pattern.
Supports OpenAI, Anthropic, and a mock provider for demos.
"""

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from app.config import settings


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""

    content: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    cost: float


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        ...


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self) -> None:
        import openai

        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start = time.time()
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        latency_ms = (time.time() - start) * 1000

        usage = response.usage
        input_tokens = usage.prompt_tokens if usage else 0
        output_tokens = usage.completion_tokens if usage else 0

        # Estimate cost (GPT-4 pricing as of 2024)
        cost = (input_tokens * 0.03 + output_tokens * 0.06) / 1000

        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=round(latency_ms, 1),
            cost=round(cost, 6),
        )


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self) -> None:
        import anthropic

        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        start = time.time()
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt if system_prompt else "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        latency_ms = (time.time() - start) * 1000

        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens * 0.003 + output_tokens * 0.015) / 1000

        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        return LLMResponse(
            content=content,
            model=self.model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=round(latency_ms, 1),
            cost=round(cost, 6),
        )


class MockProvider(LLMProvider):
    """Deterministic mock provider for demos without API keys."""

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
    ) -> LLMResponse:
        # Simulate realistic latency
        latency_ms = random.uniform(500, 2000)
        time.sleep(latency_ms / 5000)  # Brief pause for realism

        # Estimate tokens from prompt length
        input_tokens = len(prompt.split()) + len(system_prompt.split())

        # Generate contextual mock response
        content = self._generate_mock_content(prompt, system_prompt)
        output_tokens = len(content.split())

        return LLMResponse(
            content=content,
            model="mock-v1",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=round(latency_ms, 1),
            cost=0.0,
        )

    def _generate_mock_content(self, prompt: str, system_prompt: str) -> str:
        """Generate realistic mock content based on the system prompt context."""
        prompt_lower = prompt.lower()

        if "brd" in system_prompt.lower() or "business requirements" in prompt_lower:
            return self._mock_brd(prompt)
        if "trd" in system_prompt.lower() or "technical requirements" in prompt_lower:
            return self._mock_trd(prompt)
        if "functional" in system_prompt.lower():
            return self._mock_functional(prompt)
        if "design" in system_prompt.lower() or "schematic" in prompt_lower:
            return self._mock_design(prompt)
        if "recommend" in prompt_lower and "model" in prompt_lower:
            return self._mock_recommendation(prompt)
        if "raci" in prompt_lower:
            return self._mock_raci(prompt)

        return f"[Mock Response] Based on your request: {prompt[:200]}...\n\nThis is a demo response generated without an LLM API key. Configure LLM_PROVIDER=openai or LLM_PROVIDER=anthropic in your .env file for real AI-generated content."

    def _mock_brd(self, prompt: str) -> str:
        return f"""# Business Requirements Document

## Executive Summary

This document outlines the business requirements for the initiative described below. The solution aims to deliver measurable business value through AI-powered automation and intelligence.

**Initiative**: {prompt[:100]}

## Business Objectives

1. **Primary Objective**: Improve operational efficiency by 30% through intelligent automation
2. **Secondary Objective**: Reduce manual processing time by 50%
3. **Tertiary Objective**: Enable data-driven decision making across the organization

## Scope

### In Scope
- Natural language processing for document analysis
- Automated workflow orchestration
- Real-time dashboard and reporting
- Integration with existing enterprise systems

### Out of Scope
- Hardware procurement
- Network infrastructure changes
- Third-party vendor negotiations

## Stakeholders

| Role | Responsibility | Department |
|------|---------------|------------|
| Executive Sponsor | Budget approval, strategic direction | C-Suite |
| Project Manager | Day-to-day execution, timeline management | PMO |
| Technical Lead | Architecture decisions, implementation oversight | Engineering |
| Business Analyst | Requirements gathering, UAT coordination | Business Ops |

## Requirements

### Functional Requirements
1. FR-001: System shall accept natural language input for task definition
2. FR-002: System shall generate structured output documents
3. FR-003: System shall maintain audit trail of all operations
4. FR-004: System shall support role-based access control

### Non-Functional Requirements
1. NFR-001: Response time < 3 seconds for 95th percentile
2. NFR-002: System availability > 99.5%
3. NFR-003: Data encryption at rest and in transit
4. NFR-004: Compliance with SOC 2 Type II

## Acceptance Criteria
- All functional requirements pass UAT
- Performance benchmarks met in staging environment
- Security audit completed with no critical findings
- User training completed for all primary stakeholders

## Timeline
- Phase 1 (Assessment): 4 weeks
- Phase 2 (Development): 12 weeks
- Phase 3 (Testing): 4 weeks
- Phase 4 (Deployment): 2 weeks

*Generated by AI Solution Lifecycle Platform (Mock Mode)*"""

    def _mock_trd(self, prompt: str) -> str:
        return f"""# Technical Requirements Document

## Architecture Overview

**System**: {prompt[:100]}

### Technology Stack
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy
- **Frontend**: Vue3, Tailwind CSS, Pinia
- **Database**: PostgreSQL 15+
- **AI/ML**: OpenAI API / Anthropic Claude (pluggable)
- **Infrastructure**: Docker, Docker Compose

### System Architecture
```
[Client Browser] --> [Vue3 SPA] --> [FastAPI Backend] --> [PostgreSQL]
                                          |
                                    [LLM Provider]
                                    (OpenAI/Claude)
```

## API Design

### Authentication
- JWT-based authentication
- Token expiry: 24 hours
- Role-based access control (RBAC)

### Core Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/v1/auth/login | User authentication |
| GET | /api/v1/projects | List projects |
| POST | /api/v1/documents/generate | AI document generation |

## Data Model
- Normalized relational schema
- UUID primary keys for all entities
- Soft delete with archival status
- Full audit trail (created_at, updated_at, created_by)

## Security Requirements
- TLS 1.3 for all API communication
- AES-256 encryption for sensitive data at rest
- Input validation and sanitization on all endpoints
- Rate limiting: 100 requests/minute per user
- CORS restricted to approved origins

## Performance Requirements
- API response time: < 500ms (95th percentile)
- Database query time: < 100ms
- Concurrent users: 100+
- LLM generation timeout: 30 seconds

*Generated by AI Solution Lifecycle Platform (Mock Mode)*"""

    def _mock_functional(self, prompt: str) -> str:
        return f"""# Functional Specification

## Feature: {prompt[:80]}

### User Stories

**US-001**: As a project manager, I want to describe my needs in plain English so that the system generates structured documents automatically.

**US-002**: As an analyst, I want to track project milestones on a Kanban board so that I can visualize progress.

**US-003**: As a stakeholder, I want to view real-time dashboards so that I can make informed decisions.

### Process Flows

1. **Document Generation Flow**
   - User enters natural language description
   - System selects appropriate document template
   - LLM generates structured content
   - User reviews and approves/edits
   - Document versioned and stored

2. **Value Assessment Flow**
   - User inputs value component scores (0-100)
   - System calculates weighted base score
   - Readiness multiplier applied
   - Classification determined (Transformational/Strategic/Tactical/Experimental/Monitor)
   - ROI projections generated

### Business Rules
- BR-001: All documents must have at least one reviewer before approval
- BR-002: Risk scores auto-calculate from probability x impact
- BR-003: SLA breaches trigger automatic alert events
- BR-004: RACI matrix must have exactly one "A" per deliverable

*Generated by AI Solution Lifecycle Platform (Mock Mode)*"""

    def _mock_design(self, prompt: str) -> str:
        return f"""# Design Schematic

## System: {prompt[:80]}

### Component Diagram
```
+------------------+     +------------------+     +------------------+
|   Vue3 Frontend  |---->|  FastAPI Backend  |---->|   PostgreSQL DB  |
|   (Port 5173)    |     |   (Port 8000)    |     |   (Port 5432)   |
+------------------+     +------------------+     +------------------+
                                |
                         +------+------+
                         |             |
                    +----v----+  +-----v-----+
                    | OpenAI  |  | Anthropic  |
                    |   API   |  |    API     |
                    +---------+  +-----------+
```

### Data Flow
1. User interacts with Vue3 SPA
2. API calls routed through Axios client with JWT auth
3. FastAPI processes request, queries database
4. For AI features, request delegated to LLM provider
5. Response formatted and returned to client

### UI Layout
- Left sidebar: Navigation (Dashboard, Projects, Prompts, Models)
- Top bar: User menu, alert badges, project selector
- Main content: Tab-based project detail view
- Responsive grid layout with Tailwind CSS

*Generated by AI Solution Lifecycle Platform (Mock Mode)*"""

    def _mock_recommendation(self, prompt: str) -> str:
        return """Based on the use case analysis, here are the recommended AI models:

1. **GPT-4 Turbo** (Confidence: 0.92)
   - Best for: Complex document generation, nuanced analysis
   - Trade-off: Higher cost per token

2. **Claude 3.5 Sonnet** (Confidence: 0.88)
   - Best for: Long-context tasks, structured output
   - Trade-off: Slightly slower for short prompts

3. **GPT-3.5 Turbo** (Confidence: 0.75)
   - Best for: High-volume, simpler tasks
   - Trade-off: Lower quality for complex reasoning"""

    def _mock_raci(self, prompt: str) -> str:
        return """Suggested RACI assignments based on project milestones:

| Deliverable | PM | Tech Lead | Analyst | Sponsor |
|-------------|-----|-----------|---------|---------|
| Requirements Gathering | A | C | R | I |
| Architecture Design | C | R | I | A |
| Development | I | A | R | I |
| Testing | A | C | R | I |
| Deployment | A | R | C | I |
| Training | R | C | I | A |"""


class LLMProviderFactory:
    """Factory that creates the appropriate LLM provider based on settings."""

    @staticmethod
    def create(provider: Optional[str] = None) -> LLMProvider:
        provider_name = provider or settings.LLM_PROVIDER

        if provider_name == "openai":
            if not settings.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY required when LLM_PROVIDER=openai")
            return OpenAIProvider()
        elif provider_name == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY required when LLM_PROVIDER=anthropic")
            return AnthropicProvider()
        else:
            return MockProvider()


def get_llm_provider() -> LLMProvider:
    """FastAPI dependency for LLM provider."""
    return LLMProviderFactory.create()
