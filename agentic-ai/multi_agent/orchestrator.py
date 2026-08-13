"""
Multi-Agent Orchestrator
-------------------------
Routes incoming tasks to specialized agents based on intent classification.
Supports pluggable agent registration, execution tracking, and fallback logic.

Usage:
    orchestrator = AgentOrchestrator()
    orchestrator.register("research", research_agent_fn)
    orchestrator.register("code_review", code_review_agent_fn)
    result = orchestrator.dispatch("Summarize recent ML papers on anomaly detection")
"""

import logging
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .audit_logger import AuditLogger

logger = logging.getLogger(__name__)


class AgentResult:
    """Structured result from an agent execution."""

    def __init__(self, agent_name: str, output: str, metadata: Optional[Dict] = None):
        self.agent_name = agent_name
        self.output = output
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
        self.success = True
        self.error: Optional[str] = None
        self.duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "output": self.output[:500],
            "metadata": self.metadata,
            "timestamp": self.timestamp,
            "success": self.success,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


class AgentOrchestrator:
    """
    Routes tasks to registered agents and tracks execution.

    Agents are registered as callables that accept a task string
    and return a result string. The orchestrator handles routing,
    error recovery, and audit logging.
    """

    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self._agents: Dict[str, Callable[[str], str]] = {}
        self._fallback_agent: Optional[str] = None
        self._audit = audit_logger or AuditLogger()
        self._execution_history: List[AgentResult] = []

    def register(self, name: str, handler: Callable[[str], str], is_fallback: bool = False):
        self._agents[name] = handler
        if is_fallback:
            self._fallback_agent = name
        logger.info("Registered agent: %s%s", name, " (fallback)" if is_fallback else "")

    def list_agents(self) -> List[str]:
        return list(self._agents.keys())

    def dispatch(self, task: str, agent_name: Optional[str] = None) -> AgentResult:
        """
        Dispatch a task to a specific agent or auto-route.

        If agent_name is provided, routes directly. Otherwise uses
        keyword-based routing with fallback.
        """
        target = agent_name or self._route(task)

        if target not in self._agents:
            if self._fallback_agent and self._fallback_agent in self._agents:
                logger.warning("Agent '%s' not found, using fallback '%s'", target, self._fallback_agent)
                target = self._fallback_agent
            else:
                result = AgentResult(target, "")
                result.success = False
                result.error = f"No agent registered for '{target}' and no fallback available"
                self._audit.log("dispatch_failed", {"task": task[:200], "target": target})
                return result

        return self._execute(target, task)

    def _route(self, task: str) -> str:
        """Simple keyword-based routing. Replace with LLM-based classification for production."""
        task_lower = task.lower()
        for agent_name in self._agents:
            if agent_name.lower() in task_lower:
                return agent_name

        # Default to fallback or first registered agent
        if self._fallback_agent:
            return self._fallback_agent
        return next(iter(self._agents)) if self._agents else "unknown"

    def _execute(self, agent_name: str, task: str) -> AgentResult:
        result = AgentResult(agent_name, "")
        start = time.time()

        try:
            logger.info("Executing agent '%s' for task: %s", agent_name, task[:100])
            output = self._agents[agent_name](task)
            result.output = output
            result.success = True
        except Exception as e:
            logger.error("Agent '%s' failed: %s", agent_name, e)
            result.success = False
            result.error = str(e)
        finally:
            result.duration_ms = (time.time() - start) * 1000
            self._execution_history.append(result)
            self._audit.log("agent_execution", result.to_dict())

        return result

    def get_history(self, limit: int = 10) -> List[Dict]:
        return [r.to_dict() for r in self._execution_history[-limit:]]
