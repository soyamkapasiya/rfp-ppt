from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse

TRUSTED_TLDS = {"gov", "edu"}
TRUSTED_DOMAINS = {"iso.org", "nist.gov", "owasp.org", "who.int"}


def _source_trust_score(url: str) -> int:
    host = (urlparse(url).hostname or "").lower()
    if host in TRUSTED_DOMAINS:
        return 95
    if host.endswith(".gov") or host.endswith(".edu"):
        return 90
    if host:
        return 70
    return 30


def enrich_sources(rows: list[dict]) -> list[dict]:
    now = datetime.now(timezone.utc)
    enriched = []
    for row in rows:
        url = row.get("url", "")
        fetched_at = row.get("fetched_at") or now.isoformat()
        freshness_days = 0
        try:
            dt = datetime.fromisoformat(fetched_at.replace("Z", "+00:00"))
            freshness_days = max(0, int((now - dt).total_seconds() // 86400))
        except Exception:
            freshness_days = 999

        enriched.append(
            {
                **row,
                "trust_score": _source_trust_score(url),
                "freshness_days": freshness_days,
            }
        )
    return enriched
