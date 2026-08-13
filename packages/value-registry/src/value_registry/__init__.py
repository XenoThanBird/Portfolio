"""value-registry — AI opportunity value model + model registry with
mandatory evidence-class labeling.

The shared data model is the :class:`Figure`: every quantitative claim
carries an evidence class (``documented`` / ``estimated`` / ``modeled``)
and a confidence in [0, 1]. Engines refuse bare numbers
(:class:`UnclassifiedFigureError`), and reports render the class and
confidence beside every figure.
"""

from .catalog import DEFAULT_COUNT, DEFAULT_SEED, generate_catalog, write_catalog
from .evidence import (
    EvidenceClass,
    Figure,
    UnclassifiedFigureError,
    derived,
    parse_figure,
    weakest,
    weighted_aggregate,
)
from .registry import (
    RISK_DIMENSIONS,
    ApprovalState,
    Catalog,
    Hosting,
    ModelRecord,
    Provenance,
    RegistryError,
    RiskAssessment,
    assess_catalog,
    assess_risk,
    load_catalog,
)
from .report import render_portfolio_report, render_registry_report
from .rubric import Dimension, Gate, Rubric, RubricError, Stage, load_rubric
from .scoring import (
    Financials,
    GateResult,
    Opportunity,
    PortfolioError,
    ScoredOpportunity,
    load_portfolio,
    score_opportunity,
    score_portfolio,
)

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_COUNT",
    "DEFAULT_SEED",
    "RISK_DIMENSIONS",
    "ApprovalState",
    "Catalog",
    "Dimension",
    "EvidenceClass",
    "Figure",
    "Financials",
    "Gate",
    "GateResult",
    "Hosting",
    "ModelRecord",
    "Opportunity",
    "PortfolioError",
    "Provenance",
    "RegistryError",
    "RiskAssessment",
    "Rubric",
    "RubricError",
    "ScoredOpportunity",
    "Stage",
    "UnclassifiedFigureError",
    "assess_catalog",
    "assess_risk",
    "derived",
    "generate_catalog",
    "load_catalog",
    "load_portfolio",
    "load_rubric",
    "parse_figure",
    "render_portfolio_report",
    "render_registry_report",
    "score_opportunity",
    "score_portfolio",
    "weakest",
    "weighted_aggregate",
    "write_catalog",
]
