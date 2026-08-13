"""
RAG Schemas
-----------
Pydantic models for type-safe RAG pipeline I/O.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class RAGQuery(BaseModel):
    """Structured representation of an incoming user query."""
    question: str
    intent: Literal["factual", "analytical", "creative", "conversational"] = "factual"
    entities: List[str] = []
    complexity: int = Field(default=1, ge=1, le=5)
    requires_tools: bool = False
    preferred_sources: List[str] = []


class DocumentChunk(BaseModel):
    """A chunk of indexed content with metadata."""
    content: str
    chunk_id: str
    source: str
    metadata: Dict[str, Any] = {}
    embedding: Optional[List[float]] = None


class RAGResponse(BaseModel):
    """Structured response from the RAG agent."""
    answer: str
    sources: List[str] = []
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    citations: List[str] = []
    follow_up_questions: List[str] = []
    tool_calls: List[str] = []
    reasoning: Optional[str] = None


class RetrievalMetrics(BaseModel):
    """Performance metrics for the retrieval step."""
    query: str
    retrieved_count: int = 0
    relevance_scores: List[float] = []
    avg_relevance: float = 0.0
    retrieval_time: float = 0.0


class GenerationMetrics(BaseModel):
    """Performance metrics for the generation step."""
    query: str
    response: str = ""
    groundedness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    generation_time: float = 0.0
    token_usage: Dict[str, int] = {}


class RAGMetrics(BaseModel):
    """Combined metrics for a full RAG query-response cycle."""
    query_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retrieval_metrics: Optional[RetrievalMetrics] = None
    generation_metrics: Optional[GenerationMetrics] = None
    error_occurred: bool = False
    error_message: Optional[str] = None
