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
