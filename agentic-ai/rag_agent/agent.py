"""
RAG Agent
---------
LangGraph-based RAG agent with structured query analysis, vector retrieval,
optional tool augmentation, and validated response generation.

Usage:
    from rag_agent.agent import RAGAgent
    agent = RAGAgent()
    agent.index_documents(["Document text..."])
    response = agent.query("What is machine learning?")
"""

import logging
import operator
import time
import uuid
from typing import Annotated, Any, Dict, List, Optional, Sequence, TypedDict

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langgraph.graph import END, StateGraph

from .config import Config
from .schemas import RAGMetrics, RAGQuery, RAGResponse, RetrievalMetrics, GenerationMetrics
from .vector_store import FAISSVectorStore
from .tools import ArxivTool, WikipediaTool

logger = logging.getLogger(__name__)


class RAGState(TypedDict):
    query: str
    query_analysis: Optional[RAGQuery]
    retrieved_docs: List[Dict[str, Any]]
    tool_results: Dict[str, Any]
    response: Optional[RAGResponse]
    metrics: Optional[RAGMetrics]
    error_occurred: bool
    error_message: str
    messages: Annotated[Sequence[BaseMessage], operator.add]


class RAGAgent:
    """Production-ready RAG agent with LangGraph workflow."""

    def __init__(self, config: Config = None):
        self.config = config or Config()

        llm_cfg = {
            "model": self.config.get("llm", "model_name", default="gpt-4o-mini"),
            "temperature": self.config.get("llm", "temperature", default=0.1),
        }
        self.llm = ChatOpenAI(**llm_cfg)

        embed_model = self.config.get("embedding", "model_name", default="text-embedding-3-large")
        self.embeddings = OpenAIEmbeddings(model=embed_model)

        self.vector_store = FAISSVectorStore(
            dimension=self.config.get("embedding", "dimensions", default=1536),
            metric=self.config.get("vector_store", "similarity_metric", default="cosine"),
            storage_path=self.config.get("vector_store", "storage_path", default="./vector_store"),
        )

        self.tools = {}
        if self.config.get("tools", "wikipedia_enabled", default=True):
            self.tools["wikipedia"] = WikipediaTool()
        if self.config.get("tools", "arxiv_enabled", default=True):
            self.tools["arxiv"] = ArxivTool()

        self._graph = self._build_graph()

    def index_documents(self, texts: List[str], metadata: List[Dict] = None):
        embeddings = self.embeddings.embed_documents(texts)
        self.vector_store.add_documents(texts, embeddings, metadata)

    def query(self, question: str) -> RAGResponse:
        initial_state: RAGState = {
            "query": question,
            "query_analysis": None,
            "retrieved_docs": [],
            "tool_results": {},
            "response": None,
            "metrics": None,
            "error_occurred": False,
            "error_message": "",
            "messages": [HumanMessage(content=question)],
        }

        result = self._graph.invoke(initial_state)

        if result.get("response"):
            return result["response"]
        return RAGResponse(
            answer="I was unable to generate a response.",
            confidence=0.0,
        )

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(RAGState)

        graph.add_node("analyze", self._analyze_query)
        graph.add_node("retrieve", self._retrieve)
        graph.add_node("augment_tools", self._augment_with_tools)
        graph.add_node("synthesize", self._synthesize)

        graph.set_entry_point("analyze")
        graph.add_edge("analyze", "retrieve")
        graph.add_conditional_edges(
            "retrieve",
            self._should_use_tools,
            {"tools": "augment_tools", "synthesize": "synthesize"},
        )
        graph.add_edge("augment_tools", "synthesize")
        graph.add_edge("synthesize", END)

        return graph.compile()

    def _analyze_query(self, state: RAGState) -> dict:
        query = RAGQuery(question=state["query"])
        return {"query_analysis": query}

    def _retrieve(self, state: RAGState) -> dict:
        start = time.time()
        query_embedding = self.embeddings.embed_query(state["query"])
        top_k = self.config.get("retrieval", "top_k", default=5)
        threshold = self.config.get("retrieval", "similarity_threshold", default=0.7)

        docs = self.vector_store.search(query_embedding, k=top_k, threshold=threshold)
        elapsed = time.time() - start

        logger.info("Retrieved %d documents in %.2fs", len(docs), elapsed)
        return {"retrieved_docs": docs}

    def _should_use_tools(self, state: RAGState) -> str:
        analysis = state.get("query_analysis")
        if analysis and analysis.requires_tools and self.tools:
            return "tools"
        if not state.get("retrieved_docs"):
            return "tools"
        return "synthesize"

    def _augment_with_tools(self, state: RAGState) -> dict:
        results = {}
        query = state["query"]

        if "wikipedia" in self.tools:
            wiki_results = self.tools["wikipedia"].search(query)
            if wiki_results:
                results["wikipedia"] = wiki_results

        if "arxiv" in self.tools:
            arxiv_results = self.tools["arxiv"].search(query)
            if arxiv_results:
                results["arxiv"] = arxiv_results

        logger.info("Tool augmentation: %s", list(results.keys()))
        return {"tool_results": results}

    def _synthesize(self, state: RAGState) -> dict:
        start = time.time()

        context_parts = []
        sources = []
        for doc in state.get("retrieved_docs", []):
            context_parts.append(doc["content"])
            sources.append(doc.get("metadata", {}).get("source", doc.get("id", "unknown")))

        for tool_name, tool_results in state.get("tool_results", {}).items():
            for result in tool_results:
                context_parts.append(f"[{tool_name}] {result.get('title', '')}: {result.get('summary', '')}")
                if result.get("url"):
                    sources.append(result["url"])

        context = "\n\n".join(context_parts) if context_parts else "No context available."

        prompt = (
            f"Answer the following question based on the provided context. "
            f"If the context is insufficient, say so clearly.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {state['query']}\n\n"
            f"Provide a clear, well-sourced answer."
        )

        response = self.llm.invoke(prompt)
        elapsed = time.time() - start

        return {
            "response": RAGResponse(
                answer=response.content,
                sources=sources,
                confidence=min(0.9, len(context_parts) * 0.15),
                reasoning=f"Retrieved {len(state.get('retrieved_docs', []))} docs, "
                          f"used {len(state.get('tool_results', {}))} tools",
            ),
        }
