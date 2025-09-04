"""Database utility operations for the knowledge graph"""

from typing import Dict
from neo4j import Driver


class DatabaseOperations:
    """Handles database utility operations in the knowledge graph"""

    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver"""
        self.driver = driver

    def reset_database(self) -> int:
        """
        Delete all nodes and relationships in the database

        Returns:
            Number of nodes deleted
        """
        with self.driver.session() as session:
            return session.execute_write(self._reset_database_tx)

    def get_stats(self) -> Dict[str, int]:
        """
        Get basic statistics about the knowledge graph

        Returns:
            Dictionary with entity and relationship counts
        """
        with self.driver.session() as session:
            return session.execute_read(self._get_stats_tx)

    # Transaction methods
    @staticmethod
    def _reset_database_tx(tx) -> int:
        """Transaction to reset database"""
        result = tx.run("MATCH (n) DETACH DELETE n RETURN COUNT(n) AS deleted")
        return result.single()["deleted"]

    @staticmethod
    def _get_stats_tx(tx) -> Dict[str, int]:
        """Transaction to get database statistics"""
        entity_count = tx.run("MATCH (e:Entity) RETURN COUNT(e) AS count").single()[
            "count"
        ]
        rel_count = tx.run("MATCH ()-[r]->() RETURN COUNT(r) AS count").single()[
            "count"
        ]
        return {"entities": entity_count, "relationships": rel_count}
