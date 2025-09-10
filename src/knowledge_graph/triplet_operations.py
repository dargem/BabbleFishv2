"""Triplet operations for the knowledge graph"""

from typing import List, Dict, Any
from neo4j import Driver
from src.core import Triplet


class TripletOperations:
    """Handles triplet (relationship) operations in the knowledge graph"""

    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver"""
        self.driver = driver

    def add_triplets(self, triplets: List[Triplet]) -> int:
        """
        Add multiple triplets to the knowledge graph

        Args:
            triplets: List of triplets to add

        Returns:
            Number of relationships created
        """
        with self.driver.session() as session:
            return session.execute_write(self._add_triplets_tx, triplets)

    def get_entity_relationships(self, entity_name: str) -> List[Dict[str, Any]]:
        """
        Get all relationships for an entity

        Args:
            entity_name: Name of the entity

        Returns:
            List of relationships with their properties
        """
        with self.driver.session() as session:
            return session.execute_read(self._get_entity_relationships_tx, entity_name)

    def get_triplets_by_chapter(self, chapter_idx: int) -> List[Dict[str, Any]]:
        """
        Get all triplets from a specific chapter

        Args:
            chapter_idx: Chapter index

        Returns:
            List of triplets from the chapter
        """
        with self.driver.session() as session:
            return session.execute_read(self._get_triplets_by_chapter_tx, chapter_idx)

    # Transaction methods

    @staticmethod
    def _add_triplets_tx(tx, triplets: List[Triplet]) -> int:
        """Transaction to add multiple triplets"""
        query = """
        UNWIND $triplets AS triplet_data
        MATCH (subject:Entity), (object:Entity)
        WHERE triplet_data.subject_name IN subject.all_names 
        AND triplet_data.object_name IN object.all_names
        MERGE (subject)-[r:RELATES {predicate: triplet_data.predicate}]->(object)
        ON CREATE SET r += triplet_data.metadata
        RETURN COUNT(r) AS created
        """
        triplet_data = [
            {
                "subject_name": triplet.subject_name,
                "object_name": triplet.object_name,
                "predicate": triplet.predicate,
                "metadata": triplet.metadata.to_neo4j_props(),
            }
            for triplet in triplets
        ]
        result = tx.run(query, triplets=triplet_data)
        return result.single()["created"]

    @staticmethod
    def _get_entity_relationships_tx(tx, entity_name: str) -> List[Dict[str, Any]]:
        """Transaction to get entity relationships"""
        query = """
        MATCH (e:Entity)-[r]-(other:Entity)
        WHERE $entity_name IN e.all_names
        RETURN 
            properties(e) AS entity,
            type(r) AS relationship_type,
            properties(r) AS relationship_props,
            properties(other) AS related_entity,
            CASE WHEN startNode(r) = e THEN 'outgoing' ELSE 'incoming' END AS direction
        """
        result = tx.run(query, entity_name=entity_name)
        return [dict(record) for record in result]

    @staticmethod
    def _get_triplets_by_chapter_tx(tx, chapter_idx: int) -> List[Dict[str, Any]]:
        """Transaction to get triplets by chapter"""
        query = """
        MATCH (subject:Entity)-[r:RELATES]->(object:Entity)
        WHERE r.chapter_idx = $chapter_idx
        RETURN 
            subject.all_names AS subject_names,
            r.predicate AS predicate,
            object.all_names AS object_names,
            properties(r) AS metadata
        """
        result = tx.run(query, chapter_idx=chapter_idx)
        return [dict(record) for record in result]
