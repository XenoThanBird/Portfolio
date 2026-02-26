"""
Digital Twin — Quick Start Examples
Demonstrates the storage layer: vector search, knowledge graph,
privacy classification, metadata tracking, and an integrated workflow.
"""

from datetime import datetime

from storage.encryptor import DataClassifier, DataSensitivity, Encryptor
from storage.knowledge_graph import KnowledgeGraph
from storage.metadata_db import MetadataStore
from storage.vector_db import VectorStore


def _header(title: str):
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}\n")


def example_vector_search():
    """Semantic search with automatic sensitivity classification."""
    _header("Vector Database — Semantic Search")

    store = VectorStore(collection_name="quickstart_demo")

    documents = [
        {"text": "Completed the quarterly infrastructure audit with zero findings.",
         "date": "2024-01-15", "category": "operations"},
        {"text": "Deployed the ML model to production. Latency under 50ms.",
         "date": "2024-01-16", "category": "engineering"},
        {"text": "Server room temperature spiked to 85F — HVAC ticket filed.",
         "date": "2024-01-17", "category": "facilities"},
        {"text": "Team standup covered sprint goals and blockers.",
         "date": "2024-01-18", "category": "meetings"},
        {"text": "Vendor demo of the new observability platform.",
         "date": "2024-01-19", "category": "evaluation"},
    ]

    print("Adding sample records...")
    for doc in documents:
        store.add(
            documents=doc["text"],
            metadatas={"date": doc["date"], "category": doc["category"]},
        )
    print(f"Total documents: {store.count()}\n")

    for query in ["model deployment", "temperature anomaly", "team meetings"]:
        print(f"Query: '{query}'")
        results = store.query(query_texts=query, n_results=2)
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0], results["metadatas"][0], results["distances"][0],
        )):
            print(f"  {i+1}. [{meta['category']}] {doc[:60]}...  (score {1-dist:.2f})")
        print()


def example_knowledge_graph():
    """Relationship modeling with centrality analysis."""
    _header("Knowledge Graph — Relationships")

    kg = KnowledgeGraph()

    kg.add_node("person:alice", "person", {"name": "Alice", "role": "engineer"})
    kg.add_node("person:bob", "person", {"name": "Bob", "role": "analyst"})
    kg.add_node("person:charlie", "person", {"name": "Charlie", "role": "manager"})

    kg.add_node("project:pipeline", "project", {"name": "Data Pipeline"})
    kg.add_node("event:review", "event", {"name": "Design Review", "date": "2024-01-20"})

    kg.add_edge("person:alice", "project:pipeline", "works_on")
    kg.add_edge("person:bob", "project:pipeline", "works_on")
    kg.add_edge("person:charlie", "project:pipeline", "manages")
    kg.add_edge("person:alice", "event:review", "attended")
    kg.add_edge("person:charlie", "event:review", "attended")
    kg.add_edge("event:review", "project:pipeline", "related_to")

    print(f"Graph stats: {kg.stats()}\n")

    print("Design review attendees:")
    for nid, _ in kg.get_neighbors("event:review", direction="in"):
        node = kg.get_node(nid)
        print(f"  - {node.get('name')} ({node.get('role')})")

    print("\nMost connected nodes:")
    for nid, score in kg.find_central_nodes(metric="degree", top_k=3):
        node = kg.get_node(nid)
        print(f"  - {node.get('name', nid)}: {score} connections")


def example_privacy_classification():
    """Classify data sensitivity and demonstrate encryption."""
    _header("Privacy Classification & Encryption")

    samples = [
        {"text": "Server uptime was 99.97% this quarter", "type": "report", "source": "monitoring"},
        {"text": "Meeting with client at 2pm tomorrow", "type": "calendar_event", "source": "calendar"},
        {"text": "Account balance: $12,345.67", "type": "financial_transaction", "source": "ledger"},
        {"text": "Published blog post about open-source tools", "type": "content", "source": "cms"},
    ]

    for i, s in enumerate(samples, 1):
        sensitivity = DataClassifier.classify(
            data={"text": s["text"]}, data_type=s["type"], source=s["source"],
        )
        print(f"{i}. {s['text'][:50]}")
        print(f"   Sensitivity: {sensitivity.value}")
        print(f"   Encrypt: {DataClassifier.should_encrypt(sensitivity)}")
        print(f"   Storage: {DataClassifier.get_storage_location(sensitivity)}")

        if sensitivity in (DataSensitivity.HIGH, DataSensitivity.MEDIUM):
            enc = Encryptor()
            encrypted = enc.encrypt(s["text"])
            decrypted = enc.decrypt(encrypted)
            print(f"   Round-trip OK: {decrypted == s['text']}")
        print()


def example_metadata_tracking():
    """Data source registration and sync history."""
    _header("Metadata Database — Data Lineage")

    db = MetadataStore(db_url="sqlite:///data/demo_metadata.db")

    sources = [
        {"name": "erp_system", "type": "api", "freq": "daily", "config": {"endpoint": "/api/v2"}},
        {"name": "sensor_feed", "type": "webhook", "freq": "realtime", "config": {"topics": ["temp", "pressure"]}},
        {"name": "document_store", "type": "file_import", "freq": "weekly", "config": {"path": "/imports"}},
    ]

    for src in sources:
        existing = db.get_data_source(src["name"])
        if not existing:
            db.create_data_source(
                name=src["name"], source_type=src["type"],
                sync_frequency=src["freq"], config=src["config"],
            )
            print(f"Created: {src['name']}")

    print("\nActive sources:")
    for s in db.get_all_data_sources(active_only=True):
        print(f"  - {s.name} ({s.source_type}, sync: {s.sync_frequency})")

    sync = db.create_sync_record("erp_system", sync_type="incremental")
    db.complete_sync_record(sync.id, status="completed", records_added=128, records_updated=12)
    print(f"\nSync completed: 128 added, 12 updated")

    print(f"\nSystem stats: {db.get_stats()}")


def example_integrated_workflow():
    """End-to-end: ingest a record through all storage layers."""
    _header("Integrated Workflow")

    db = MetadataStore(db_url="sqlite:///data/demo_metadata.db")
    vs = VectorStore(collection_name="integrated_demo")
    kg = KnowledgeGraph()
    enc = Encryptor()

    record = {
        "from": "ops-team@example.com",
        "subject": "Pipeline Deployment Complete",
        "body": "The data pipeline v2.1 deployed successfully. All health checks passing.",
        "date": "2024-01-20T10:30:00",
        "source": "erp_system",
    }

    print("1. Classifying and storing record...")
    sensitivity = DataClassifier.classify(
        data=record, data_type="document", source=record["source"],
    )
    print(f"   Sensitivity: {sensitivity.value}")

    content_hash = enc.hash_data(record["body"])
    db.create_data_record(
        data_source_name="erp_system", content_hash=content_hash,
        record_type="document", sensitivity=sensitivity.value,
        title=record["subject"],
        record_timestamp=datetime.fromisoformat(record["date"]),
    )
    print("   Metadata record created")

    vs.add(
        documents=f"Subject: {record['subject']}\n{record['body']}",
        metadatas={"type": "document", "date": record["date"], "subject": record["subject"]},
    )
    print("   Added to vector store")

    kg.add_node(f"entity:{record['from']}", "entity", {"email": record["from"]})
    kg.add_node(f"doc:{content_hash[:16]}", "document", {"subject": record["subject"]})
    kg.add_edge(f"entity:{record['from']}", f"doc:{content_hash[:16]}", "authored")
    print("   Added to knowledge graph")

    print("\n2. Querying...")
    results = vs.query("pipeline deployment status", n_results=1)
    if results["documents"][0]:
        print(f"   Vector hit: {results['metadatas'][0][0]['subject']}")

    neighbors = kg.get_neighbors(f"entity:{record['from']}", edge_type="authored")
    print(f"   Graph: {len(neighbors)} document(s) by {record['from']}")

    print("\nWorkflow complete.")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Digital Twin — Quick Start Examples")
    print("=" * 60)

    example_vector_search()
    example_knowledge_graph()
    example_privacy_classification()
    example_metadata_tracking()
    example_integrated_workflow()

    print("\nAll examples complete.")
