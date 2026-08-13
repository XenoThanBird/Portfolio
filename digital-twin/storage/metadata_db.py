"""
SQLAlchemy ORM models for metadata storage and data lineage tracking.
Tracks data sources, sync history, records, and generated insights.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, Session

Base = declarative_base()


class DataSource(Base):
    """Track connected data sources and their sync status."""

    __tablename__ = "data_sources"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(50), nullable=False)          # "api", "file_import", "webhook"
    is_active = Column(Boolean, default=True)
    is_connected = Column(Boolean, default=False)

    credentials_path = Column(String(500))
    api_key_hash = Column(String(256))

    sync_frequency = Column(String(50))                       # "daily", "weekly", "manual"
    last_sync_at = Column(DateTime)
    next_sync_at = Column(DateTime)
    sync_enabled = Column(Boolean, default=True)

    total_records = Column(Integer, default=0)
    total_size_bytes = Column(Integer, default=0)
    last_error = Column(Text)
    error_count = Column(Integer, default=0)

    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sync_history = relationship("SyncHistory", back_populates="data_source", cascade="all, delete-orphan")
    records = relationship("DataRecord", back_populates="data_source", cascade="all, delete-orphan")


class SyncHistory(Base):
    """Track sync operations and their results."""

    __tablename__ = "sync_history"

    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)

    started_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    status = Column(String(50))                               # "running", "completed", "failed"

    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    bytes_processed = Column(Integer, default=0)

    error_message = Column(Text)
    error_details = Column(JSON)

    sync_type = Column(String(50))                            # "full", "incremental", "manual"
    metadata = Column(JSON)

    data_source = relationship("DataSource", back_populates="sync_history")


class DataRecord(Base):
    """Track individual data records and their storage locations."""

    __tablename__ = "data_records"

    id = Column(Integer, primary_key=True)
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)

    external_id = Column(String(256))
    content_hash = Column(String(256), unique=True, nullable=False)

    record_type = Column(String(100))                         # "document", "event", "record"
    data_category = Column(String(50))                        # "communication", "operations", etc.
    sensitivity = Column(String(20))                          # "high", "medium", "low", "public"

    vector_db_id = Column(String(256))
    graph_db_id = Column(String(256))
    encrypted_path = Column(String(500))

    title = Column(String(500))
    description = Column(Text)
    tags = Column(JSON)
    entities = Column(JSON)

    record_timestamp = Column(DateTime)
    ingested_at = Column(DateTime, default=datetime.utcnow)

    is_processed = Column(Boolean, default=False)
    is_embedded = Column(Boolean, default=False)
    is_indexed = Column(Boolean, default=False)

    metadata = Column(JSON)
    size_bytes = Column(Integer)

    data_source = relationship("DataSource", back_populates="records")


class InsightRecord(Base):
    """Store generated insights and detected patterns."""

    __tablename__ = "insights"

    id = Column(Integer, primary_key=True)

    insight_type = Column(String(100))                        # "pattern", "anomaly", "trend"
    category = Column(String(100))
    title = Column(String(500))
    description = Column(Text)
    confidence = Column(Float)

    supporting_records = Column(JSON)
    data_range_start = Column(DateTime)
    data_range_end = Column(DateTime)

    is_actionable = Column(Boolean, default=False)
    suggested_actions = Column(JSON)
    priority = Column(String(20))

    is_viewed = Column(Boolean, default=False)
    is_dismissed = Column(Boolean, default=False)
    user_feedback = Column(String(20))

    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class MetadataStore:
    """
    High-level interface for metadata database operations.
    Wraps SQLAlchemy session management for data source tracking,
    sync history, record lineage, and insight storage.
    """

    def __init__(self, db_url: str = "sqlite:///data/metadata.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        return self.SessionLocal()

    # --- data source operations ---

    def create_data_source(
        self, name: str, source_type: str,
        sync_frequency: str = "daily", config: Optional[Dict] = None,
    ) -> DataSource:
        with self.get_session() as session:
            source = DataSource(
                name=name, source_type=source_type,
                sync_frequency=sync_frequency, config=config or {},
            )
            session.add(source)
            session.commit()
            session.refresh(source)
            return source

    def get_data_source(self, name: str) -> Optional[DataSource]:
        with self.get_session() as session:
            return session.query(DataSource).filter_by(name=name).first()

    def get_all_data_sources(self, active_only: bool = False) -> List[DataSource]:
        with self.get_session() as session:
            query = session.query(DataSource)
            if active_only:
                query = query.filter_by(is_active=True)
            return query.all()

    # --- sync history ---

    def create_sync_record(self, data_source_name: str, sync_type: str = "incremental") -> SyncHistory:
        with self.get_session() as session:
            source = session.query(DataSource).filter_by(name=data_source_name).first()
            if not source:
                raise ValueError(f"Data source not found: {data_source_name}")
            record = SyncHistory(
                data_source_id=source.id,
                started_at=datetime.utcnow(),
                status="running",
                sync_type=sync_type,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def complete_sync_record(
        self, sync_id: int, status: str,
        records_added: int = 0, records_updated: int = 0,
        error_message: Optional[str] = None,
    ):
        with self.get_session() as session:
            rec = session.query(SyncHistory).filter_by(id=sync_id).first()
            if rec:
                rec.completed_at = datetime.utcnow()
                rec.status = status
                rec.records_added = records_added
                rec.records_updated = records_updated
                rec.error_message = error_message
                session.commit()

    # --- data records ---

    def create_data_record(
        self, data_source_name: str, content_hash: str,
        record_type: str, sensitivity: str, **kwargs,
    ) -> DataRecord:
        with self.get_session() as session:
            source = session.query(DataSource).filter_by(name=data_source_name).first()
            if not source:
                raise ValueError(f"Data source not found: {data_source_name}")
            record = DataRecord(
                data_source_id=source.id,
                content_hash=content_hash,
                record_type=record_type,
                sensitivity=sensitivity,
                **kwargs,
            )
            session.add(record)
            session.commit()
            session.refresh(record)
            return record

    def get_data_records(
        self, data_source_name: Optional[str] = None,
        record_type: Optional[str] = None,
        sensitivity: Optional[str] = None,
        limit: int = 100,
    ) -> List[DataRecord]:
        with self.get_session() as session:
            query = session.query(DataRecord)
            if data_source_name:
                source = session.query(DataSource).filter_by(name=data_source_name).first()
                if source:
                    query = query.filter_by(data_source_id=source.id)
            if record_type:
                query = query.filter_by(record_type=record_type)
            if sensitivity:
                query = query.filter_by(sensitivity=sensitivity)
            return query.order_by(DataRecord.ingested_at.desc()).limit(limit).all()

    # --- insights ---

    def create_insight(
        self, insight_type: str, category: str,
        title: str, description: str, confidence: float, **kwargs,
    ) -> InsightRecord:
        with self.get_session() as session:
            insight = InsightRecord(
                insight_type=insight_type, category=category,
                title=title, description=description,
                confidence=confidence, **kwargs,
            )
            session.add(insight)
            session.commit()
            session.refresh(insight)
            return insight

    def get_insights(
        self, category: Optional[str] = None,
        unviewed_only: bool = False, limit: int = 20,
    ) -> List[InsightRecord]:
        with self.get_session() as session:
            query = session.query(InsightRecord).filter_by(is_dismissed=False)
            if category:
                query = query.filter_by(category=category)
            if unviewed_only:
                query = query.filter_by(is_viewed=False)
            return query.order_by(InsightRecord.created_at.desc()).limit(limit).all()

    # --- statistics ---

    def get_stats(self) -> Dict[str, Any]:
        with self.get_session() as session:
            return {
                "total_data_sources": session.query(DataSource).count(),
                "active_data_sources": session.query(DataSource).filter_by(is_active=True).count(),
                "total_records": session.query(DataRecord).count(),
                "total_insights": session.query(InsightRecord).filter_by(is_dismissed=False).count(),
            }
