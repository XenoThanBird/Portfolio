"""AI Solution Lifecycle Platform — FastAPI Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings as app_settings
from app.database import engine
from app.models import Base
from app.routers import (
    alerts,
    auth,
    dashboard,
    documents,
    milestones,
    model_catalog,
    prompts,
    raci,
    risks,
    sla,
    value,
)
from app.routers import projects as projects_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create tables on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Solution Lifecycle Platform",
    description=(
        "End-to-end platform for evaluating, planning, and managing "
        "AI solution deployments — from value assessment through production monitoring."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=app_settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(projects_router.router)
app.include_router(documents.router)
app.include_router(prompts.router)
app.include_router(milestones.router)
app.include_router(raci.router)
app.include_router(sla.router)
app.include_router(alerts.router)
app.include_router(risks.router)
app.include_router(model_catalog.router)
app.include_router(value.router)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}
