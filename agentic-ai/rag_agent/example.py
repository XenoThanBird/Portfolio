"""
RAG Agent — Usage Example
--------------------------
Demonstrates basic document indexing and querying with the RAG agent.

Usage:
    export OPENAI_API_KEY=sk-...
    python -m rag_agent.example
"""

from rag_agent.agent import RAGAgent
from rag_agent.config import Config


def main():
    # Initialize with default config
    config = Config("rag_agent/config.yaml")
    agent = RAGAgent(config)

    # Index sample documents
    documents = [
        "Retrieval-Augmented Generation (RAG) combines a retrieval system with a "
        "generative model. The retriever fetches relevant documents from a knowledge "
        "base, and the generator produces an answer grounded in that context.",

        "FAISS (Facebook AI Similarity Search) is a library for efficient similarity "
        "search and clustering of dense vectors. It supports billion-scale datasets "
        "and multiple index types including flat, IVF, and HNSW.",

        "LangGraph extends LangChain with a graph-based execution model. Nodes "
        "represent processing steps, and edges define the flow. Conditional edges "
        "enable dynamic routing based on intermediate state.",

        "Vector embeddings represent text as high-dimensional numeric vectors. "
        "Similar texts produce vectors that are close together in embedding space, "
        "enabling semantic search beyond simple keyword matching.",
    ]

    metadata = [
        {"source": "rag_overview.md", "topic": "RAG"},
        {"source": "faiss_docs.md", "topic": "vector_search"},
        {"source": "langgraph_guide.md", "topic": "orchestration"},
        {"source": "embeddings_primer.md", "topic": "embeddings"},
    ]

    print("Indexing documents...")
    agent.index_documents(documents, metadata)
    print(f"Vector store: {agent.vector_store.get_stats()}")

    # Query
    questions = [
        "What is RAG and how does it work?",
        "How does FAISS handle similarity search?",
        "What are vector embeddings used for?",
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        response = agent.query(question)
        print(f"A: {response.answer[:300]}...")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Sources: {response.sources}")


if __name__ == "__main__":
    main()
