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

    def hybrid_retrieve(self, query_text: str, top_k: int = 15) -> list[dict]:
        """Hybrid Vector + Graph retrieval with Cross-Encoder Reranking."""
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

        # ── BGE-Reranker Optimization (The Token Cost Trap) ──────────────────
        # Instead of feeding 15 docs to LLM, we rerank and pick top 5.
        # This reduces noise and token cost significantly.
        return self._rerank(query_text, merged, limit=5)

    def _rerank(self, query: str, docs: list[dict], limit: int = 5) -> list[dict]:
        """Cross-encoder reranking simulation (Conceptual BGE-Reranker)."""
        if not docs:
            return []
            
        def calculate_relevance(row: dict) -> float:
            # Combined score: Vector Sim + Internal Trust + Freshness
            base_score = row.get("score", 0.5)
            trust_multiplier = 1.5 if row.get("source_type") == "internal_vault" else 1.0
            freshness_penalty = (row.get("freshness_days", 0) / 365) * 0.1
            return (base_score * trust_multiplier) - freshness_penalty

        ranked = sorted(docs, key=calculate_relevance, reverse=True)
        return ranked[:limit]
