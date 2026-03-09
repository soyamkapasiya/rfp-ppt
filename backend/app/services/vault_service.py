import logging
from pathlib import Path
from app.db.chroma import ChromaStore
from app.db.neo4j import Neo4jStore
from app.services.source_quality_service import enrich_sources

logger = logging.getLogger(__name__)

class VaultService:
    """Handles ingestion of company secret sauce: past winning bids, PDFs, etc."""
    def __init__(self, chroma: ChromaStore, neo4j: Neo4jStore):
        self.chroma = chroma
        self.neo4j = neo4j

    def ingest_local_file(self, file_path: str, win_reason: str = "Technical Depth", win_rate: float = 0.8):
        path = Path(file_path)
        if not path.exists():
            logger.error("Vault file missing: %s", file_path)
            return

        # Simplified PDF/Text extraction logic
        content = path.read_text(errors="ignore", encoding="utf-8")
        
        doc = {
            "id": f"vault-{path.stem}",
            "title": path.name,
            "content": content,
            "url": str(path.absolute()),
            "source_type": "internal_vault",
            "trust_score": 1.0,
            "freshness_days": 0,
            "win_reason": win_reason,
            "win_rate": win_rate
        }
        
        enriched = enrich_sources([doc])
        self.chroma.add_documents(enriched)
        self.neo4j.upsert_entity("InternalDocument", "name", path.name, {
            "path": str(path),
            "win_reason": win_reason,
            "win_rate": win_rate
        })
        logger.info("Vault ingested: %s with win_reason: %s", path.name, win_reason)

    def ingest_correction(self, slide_title: str, corrected_content: str, project_name: str):
        """Learning Loop: Ingest human-edited content back into the Vault."""
        doc = {
            "id": f"correction-{slide_title}",
            "title": f"Human Corrected: {slide_title} ({project_name})",
            "content": corrected_content,
            "source_type": "internal_vault",
            "trust_score": 2.0,  # Highest trust for human-in-the-loop edits
            "freshness_days": 0
        }
        self.chroma.add_documents([doc])
        logger.info("Learning loop: Ingested correction for %s", slide_title)

    def query_vault(self, query: str, top_k: int = 5):
        # Query specifically for internal documents
        return self.chroma.query(query, top_k=top_k, where={"source_type": "internal_vault"})
