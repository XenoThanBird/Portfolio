"""
Async HTTP Client
------------------
Reusable HTTP client with exponential backoff retry logic.
Designed for integrating external APIs into MCP tool handlers.
"""

import asyncio
import logging
from typing import Any, Optional

import httpx

from .config import settings

logger = logging.getLogger(__name__)


async def make_request(
    url: str,
    method: str = "GET",
    params: Optional[dict] = None,
    headers: Optional[dict] = None,
) -> Optional[dict[str, Any]]:
    """
    Make an HTTP request with automatic retry and exponential backoff.

    Returns parsed JSON on success, None on failure.
    """
    default_headers = {
        "User-Agent": settings.user_agent,
        "Accept": "application/json",
    }
    if headers:
        default_headers.update(headers)

    attempt = 0
    backoff = settings.backoff_seconds

    async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
        while attempt < settings.max_retries:
            try:
                resp = await client.request(method, url, params=params, headers=default_headers)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                attempt += 1
                logger.warning("Attempt %d/%d failed for %s: %s", attempt, settings.max_retries, url, e)
                if attempt >= settings.max_retries:
                    logger.error("All retries exhausted for %s", url)
                    return None
                await asyncio.sleep(backoff)
                backoff *= 2
