"""
neo4j.py – Neo4j graph store with graceful fallback.

If Neo4j is unavailable (e.g., in local dev), all operations silently
no-op so the rest of the pipeline continues unaffected.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    from neo4j.exceptions import ServiceUnavailable
except ImportError:
    GraphDatabase = None  # type: ignore
    ServiceUnavailable = Exception  # type: ignore


class Neo4jStore:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = None
        if not GraphDatabase:
            return
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verify connection is actually available
            driver.verify_connectivity()
            self.driver = driver
            logger.info("Neo4j connected: %s", uri)
        except Exception as exc:
            logger.warning(
                "Neo4j unavailable at %s – graph features disabled. Error: %s",
                uri, exc,
            )

    def upsert_entity(self, label: str, key: str, name: str, props: dict | None = None) -> None:
        if not self.driver:
            return
        try:
            query = f"""
            MERGE (n:{label} {{{key}: $name}})
            SET n += $props
            """
            with self.driver.session() as session:
                session.run(query, name=name, props=props or {})
        except Exception as exc:
            logger.debug("Neo4j upsert_entity failed (non-fatal): %s", exc)

    def query_related(self, query_text: str, top_k: int = 5) -> list[dict]:
        if not self.driver:
            return []
        try:
            query = """
            MATCH (d:Document)
            WHERE toLower(d.name) CONTAINS toLower($query_text)
            RETURN d.name AS title, d.url AS url
            LIMIT $top_k
            """
            rows = []
            with self.driver.session() as session:
                for row in session.run(query, query_text=query_text, top_k=top_k):
                    rows.append({
                        "id": row["title"],
                        "title": row["title"],
                        "url": row["url"],
                        "score": 0.7,
                    })
            return rows
        except Exception as exc:
            logger.debug("Neo4j query_related failed (non-fatal): %s", exc)
            return []

    def close(self) -> None:
        if self.driver:
            try:
                self.driver.close()
            except Exception:
                pass
