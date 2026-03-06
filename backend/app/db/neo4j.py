from __future__ import annotations

try:
    from neo4j import GraphDatabase
except ImportError:
    GraphDatabase = None


class Neo4jStore:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password)) if GraphDatabase else None

    def upsert_entity(self, label: str, key: str, name: str, props: dict | None = None) -> None:
        if not self.driver:
            return

        query = f"""
        MERGE (n:{label} {{{key}: $name}})
        SET n += $props
        """
        with self.driver.session() as session:
            session.run(query, name=name, props=props or {})

    def query_related(self, query_text: str, top_k: int = 5) -> list[dict]:
        if not self.driver:
            return []

        query = """
        MATCH (d:Document)
        WHERE toLower(d.name) CONTAINS toLower($query_text)
        RETURN d.name AS title, d.url AS url
        LIMIT $top_k
        """
        rows = []
        with self.driver.session() as session:
            for row in session.run(query, query_text=query_text, top_k=top_k):
                rows.append({"id": row["title"], "title": row["title"], "url": row["url"], "score": 0.7})
        return rows
