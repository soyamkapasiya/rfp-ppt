from __future__ import annotations

from pathlib import Path

try:
    import chromadb
except ImportError:
    chromadb = None


class ChromaStore:
    def __init__(self, persist_dir: str):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_dir)) if chromadb else None
        self.collection = self.client.get_or_create_collection("rfp_docs") if self.client else None

    def add_documents(self, docs: list[dict]) -> None:
        if not self.collection:
            return

        ids = []
        documents = []
        metadatas = []
        for idx, doc in enumerate(docs):
            ids.append(doc.get("id") or f"doc-{idx}")
            documents.append(doc.get("text") or doc.get("content") or "")
            metadatas.append({"url": doc.get("url", ""), "title": doc.get("title", "")})

        if ids:
            self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)

    def query(self, query_text: str, top_k: int = 5) -> list[dict]:
        if not self.collection:
            return []

        result = self.collection.query(query_texts=[query_text], n_results=top_k)
        docs = result.get("documents", [[]])[0]
        metas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        rows = []
        for idx, text in enumerate(docs):
            meta = metas[idx] if idx < len(metas) else {}
            distance = distances[idx] if idx < len(distances) else 1
            rows.append(
                {
                    "id": f"vector-{idx}",
                    "text": text,
                    "url": (meta or {}).get("url", ""),
                    "title": (meta or {}).get("title", ""),
                    "score": max(0, 1 - float(distance)),
                }
            )
        return rows
