# 09 — Digital Twin: Multi-Database Architecture

A privacy-first digital twin framework demonstrating multi-database architecture with encrypted vector search, knowledge graph analysis, and metadata lineage tracking.

## Architecture

This module showcases a **three-database storage layer** with sensitivity-based encryption routing:

| Database | Technology | Purpose |
| -------- | ---------- | ------- |
| Vector Store | ChromaDB + Sentence Transformers | Semantic search with automatic sensitivity classification |
| Knowledge Graph | NetworkX (MultiDiGraph) | Entity relationships, centrality analysis, community detection |
| Metadata DB | SQLAlchemy + SQLite | Data source tracking, sync history, record lineage |

All three layers integrate with a **Fernet (AES-256) encryption layer** that automatically classifies data sensitivity (HIGH / MEDIUM / LOW / PUBLIC) and routes storage accordingly.

## Files

| File | Description |
| ---- | ----------- |
| `storage/vector_db.py` | ChromaDB wrapper with encryption-aware add/query |
| `storage/knowledge_graph.py` | NetworkX graph with centrality, path-finding, temporal queries |
| `storage/metadata_db.py` | SQLAlchemy ORM for data sources, sync history, insights |
| `storage/encryptor.py` | Fernet encryption + sensitivity classifier |
| `config.py` | Pydantic BaseSettings configuration management |
| `example.py` | Five runnable examples demonstrating the full stack |
| `architecture.md` | Detailed architecture documentation |

## Quick Start

```bash
# Install dependencies
pip install chromadb networkx sqlalchemy cryptography pydantic-settings sentence-transformers

# Run the examples
cd 09_digital_twin
python example.py
```

## Key Patterns Demonstrated

- **Privacy-by-design**: Automatic sensitivity classification with keyword and type-based rules
- **Encrypted search**: Sensitive content is encrypted at rest while embeddings remain searchable
- **Multi-database coordination**: Vector, graph, and relational stores working together
- **Data lineage**: Full tracking from source registration through sync to individual records
- **Graph analytics**: Centrality metrics, community detection, temporal queries, path-finding
- **Production config**: Pydantic BaseSettings with env-var overrides and typed validation
