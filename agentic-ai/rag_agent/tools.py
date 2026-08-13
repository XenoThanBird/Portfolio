"""
RAG External Tools
-------------------
Tool integrations for augmenting RAG responses with live data.
Each tool is rate-limited and cached to avoid API abuse.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter with minimum delay between calls."""

    def __init__(self, min_delay: float = 0.2):
        self.min_delay = min_delay
        self._last_call = 0.0

    def wait(self):
        elapsed = time.time() - self._last_call
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self._last_call = time.time()


class WikipediaTool:
    """Search Wikipedia for factual context."""

    BASE_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"
    SEARCH_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self, max_results: int = 3):
        self.max_results = max_results
        self._limiter = RateLimiter(0.1)
        self._cache: Dict[str, Any] = {}

    def search(self, query: str) -> List[Dict[str, str]]:
        if query in self._cache:
            return self._cache[query]

        self._limiter.wait()
        try:
            resp = requests.get(self.SEARCH_URL, params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": self.max_results,
                "format": "json",
            }, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            results = []
            for item in data.get("query", {}).get("search", []):
                title = item["title"]
                summary = self._get_summary(title)
                if summary:
                    results.append({
                        "title": title,
                        "summary": summary,
                        "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
                    })

            self._cache[query] = results
            return results
        except Exception as e:
            logger.warning("Wikipedia search failed: %s", e)
            return []

    def _get_summary(self, title: str) -> Optional[str]:
        self._limiter.wait()
        try:
            resp = requests.get(f"{self.BASE_URL}/{title}", timeout=10)
            if resp.ok:
                return resp.json().get("extract", "")
        except Exception:
            pass
        return None


class ArxivTool:
    """Search ArXiv for academic papers."""

    BASE_URL = "http://export.arxiv.org/api/query"

    def __init__(self, max_results: int = 3):
        self.max_results = max_results
        self._limiter = RateLimiter(0.5)

    def search(self, query: str) -> List[Dict[str, str]]:
        self._limiter.wait()
        try:
            resp = requests.get(self.BASE_URL, params={
                "search_query": f"all:{query}",
                "max_results": self.max_results,
                "sortBy": "relevance",
            }, timeout=15)
            resp.raise_for_status()

            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            results = []
            for entry in root.findall("atom:entry", ns):
                results.append({
                    "title": entry.find("atom:title", ns).text.strip(),
                    "summary": entry.find("atom:summary", ns).text.strip()[:500],
                    "url": entry.find("atom:id", ns).text.strip(),
                    "authors": [
                        a.find("atom:name", ns).text
                        for a in entry.findall("atom:author", ns)
                    ],
                })
            return results
        except Exception as e:
            logger.warning("ArXiv search failed: %s", e)
            return []
