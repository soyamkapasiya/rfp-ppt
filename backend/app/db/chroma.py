class ChromaStore:
    def __init__(self, persist_dir: str):
        self.persist_dir = persist_dir

    def add_documents(self, docs: list[dict]) -> None:
        _ = docs

    def query(self, query_text: str, top_k: int = 5) -> list[dict]:
        _ = query_text
        _ = top_k
        return []
