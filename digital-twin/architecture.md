# Digital Twin Architecture

## Overview

A multi-database digital twin system that aggregates data from multiple sources, builds a comprehensive model of entities and relationships, and provides predictive insights through privacy-first storage patterns.

## Core Principles

1. **Privacy First**: Sensitive data is encrypted at rest with sensitivity-based routing
2. **Modularity**: Plug-in data sources with standardized connectors
3. **Explainability**: All predictions come with reasoning and supporting evidence
4. **Scalability**: Designed for years of multi-source data accumulation
5. **Real-time**: Support for streaming data ingestion via webhooks

## System Architecture

```text
┌─────────────────────────────────────────────────────────────┐
│                     Data Sources Layer                       │
├─────────────────────────────────────────────────────────────┤
│  APIs  |  File Imports  |  Webhooks  |  Manual Exports      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Connector Layer                            │
├─────────────────────────────────────────────────────────────┤
│  • Plugin-based architecture                                 │
│  • OAuth / API key management                                │
│  • Rate limiting & retry logic                               │
│  • Incremental sync support                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Processing Layer                            │
├─────────────────────────────────────────────────────────────┤
│  Text Processor | Entity Extractor | Sentiment Analyzer      │
│  Timeline Builder | Topic Modeler                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                              │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Vector DB   │  │ Knowledge    │  │  Metadata    │      │
│  │  (ChromaDB)  │  │ Graph (NX)   │  │  DB (SQLite) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  Storage Strategy:                                           │
│  • HIGH sensitivity  →  Encrypted local storage              │
│  • MEDIUM sensitivity →  Local database (encrypted)          │
│  • LOW / PUBLIC       →  Standard storage                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Interface Layer                             │
├─────────────────────────────────────────────────────────────┤
│  • REST API (FastAPI)                                        │
│  • CLI Interface                                             │
│  • WebSocket for real-time queries                           │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### Ingestion Pipeline

```text
Source → Connector → Validator → Processor → Enrichment → Storage
                                                              ↓
                                                    Privacy Classifier
                                                              ↓
                                              Sensitive?  →  Encrypted local
                                              General?    →  Standard DB
```

### Query Pipeline

```text
User Query → Intent Parser → Context Retriever → Reasoning → Response
                                    ↓
                          [Vector Search + Graph Traversal]
```

## Privacy & Security Model

### Data Classification

1. **HIGH Sensitivity**: Private messages, financial records, credentials
   - Storage: Encrypted local
   - Encryption: Fernet (AES-256) at rest
   - Access: Requires decryption key

2. **MEDIUM Sensitivity**: Calendar events, internal documents
   - Storage: Local encrypted database
   - Indexed by hash for queries

3. **LOW / PUBLIC**: General records, published content
   - Storage: Standard database
   - Used for fast retrieval

### Encryption Strategy

```python
raw_data → classify() → encrypt(Fernet) → store(local) → index(metadata_only)
                                                              ↓
                                                    Vector embedding (searchable)
```

## Technology Stack

| Layer | Technology | Purpose |
| ----- | ---------- | ------- |
| Vector DB | ChromaDB | Semantic search with local persistence |
| Knowledge Graph | NetworkX | Relationship modeling and centrality analysis |
| Metadata DB | SQLAlchemy + SQLite | Data lineage and sync tracking |
| Encryption | cryptography (Fernet) | AES-256 symmetric encryption |
| Embeddings | Sentence Transformers | Local text embeddings |
| Configuration | Pydantic BaseSettings | Typed env-var management |
| API | FastAPI | Async REST endpoints |

## Key Design Decisions

### Why Hybrid Storage?

- **Privacy**: Sensitive data stays encrypted locally
- **Performance**: Vector search for semantic queries, graph for relationships
- **Flexibility**: Each storage layer can be upgraded independently

### Why Knowledge Graph?

- **Relationships**: "Which entities are connected to this event?"
- **Context**: Richer than pure vector similarity
- **Insights**: Detect patterns across domains via centrality and community detection

### Why Sensitivity Classification?

- **Automated routing**: Data goes to the right storage tier automatically
- **Compliance**: Clear audit trail for what is encrypted and where
- **Extensibility**: Add new sensitivity rules without changing storage logic

## Scaling Considerations

### Storage Growth

- **Embeddings**: ~10 GB per million documents (all-MiniLM-L6-v2)
- **Graph**: Millions of nodes/edges with NetworkX; upgrade to Neo4j at scale
- **Metadata**: SQLite handles millions of rows; migrate to PostgreSQL for concurrency

### Query Performance

- **Vector Search**: < 100 ms for 1M documents (ChromaDB)
- **Graph Traversal**: < 500 ms for relationship queries
- **Full Pipeline**: Target < 2 s for complex multi-store queries
