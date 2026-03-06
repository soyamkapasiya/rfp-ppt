from __future__ import annotations

from app.db.chroma import ChromaStore
from app.db.neo4j import Neo4jStore


class GraphRAGService:
    def __init__(self, chroma: ChromaStore, neo4j: Neo4jStore):
        self.chroma = chroma
        self.neo4j = neo4j

    def ingest_documents(self, docs: list[dict]) -> None:
        self.chroma.add_documents(docs)
        for doc in docs:
            title = doc.get("title") or doc.get("url", "unknown")
            self.neo4j.upsert_entity("Document", "name", title, {"url": doc.get("url", "")})

    def hybrid_retrieve(self, query_text: str, top_k: int = 8) -> list[dict]:
        vector_hits = self.chroma.query(query_text, top_k=top_k)
        graph_hits = self.neo4j.query_related(query_text, top_k=top_k)

        merged = []
        seen = set()
        for item in vector_hits + graph_hits:
            key = item.get("url") or item.get("id") or str(item)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)

        def rank_score(row: dict) -> tuple:
            return (
                row.get("trust_score", 0),
                -row.get("freshness_days", 9999),
                row.get("score", 0),
            )

        return sorted(merged, key=rank_score, reverse=True)[:top_k]
