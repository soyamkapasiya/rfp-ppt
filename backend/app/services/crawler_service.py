from __future__ import annotations

from datetime import datetime, timezone

import httpx


class CrawlerService:
    def __init__(self, timeout_s: int = 10):
        self.timeout_s = timeout_s

    def fetch_url(self, url: str) -> dict:
        try:
            with httpx.Client(timeout=self.timeout_s, follow_redirects=True) as client:
                response = client.get(url)
                text = response.text[:10000]
                return {
                    "url": str(response.url),
                    "status": response.status_code,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "text": text,
                }
        except Exception:
            return {
                "url": url,
                "status": 0,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "text": "",
            }

    def fetch_many(self, urls: list[str]) -> list[dict]:
        return [self.fetch_url(url) for url in urls]
