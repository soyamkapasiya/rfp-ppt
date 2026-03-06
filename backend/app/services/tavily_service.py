from __future__ import annotations

from typing import Any

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None


class TavilyService:
    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key=api_key) if TavilyClient and api_key else None

    def search(self, query: str, max_results: int = 8) -> list[dict[str, Any]]:
        if not self.client:
            return [
                {
                    "title": "Placeholder source",
                    "url": "https://example.com/placeholder",
                    "content": f"No Tavily API key configured for query: {query}",
                }
            ]

        response = self.client.search(query=query, search_depth="advanced", max_results=max_results)
        return response.get("results", [])
