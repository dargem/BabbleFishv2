"""Triplet operations for the knowledge graph"""

from typing import List
from neo4j import Driver
from src.core import InputTriplet
from .utils import create_triplet_from_dict, check_not_incoming


class TripletOperations:
    """Handles triplet (relationship) operations in the knowledge graph"""

    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver"""
        self.driver = driver

    def add_triplets(self, triplets: List[InputTriplet]) -> int:
        """
        Add multiple triplets to the knowledge graph

        Args:
            triplets: List of triplets to add

        Returns:
            Number of relationships created
        """
        with self.driver.session() as session:
            return session.execute_write(self._add_triplets_tx, triplets)

    def get_entity_relationships(self, entity_name: str) -> List[InputTriplet]:
        """
        Get all relationships for an entity

        Args:
            entity_name: Name of the entity

        Returns:
            List of relationships with their properties
        """
        with self.driver.session() as session:
            return session.execute_read(self._get_entity_relationships_tx, entity_name)

    def get_triplets_by_chapter(self, chapter_idx: int) -> List[InputTriplet]:
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
    def _add_triplets_tx(tx, triplets: List[InputTriplet]) -> int:
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
    def _get_entity_relationships_tx(tx, entity_name: str) -> List[InputTriplet]:
        """Transaction to get entity relationships"""
        query = """
        MATCH (e:Entity)-[r:RELATES]-(other:Entity)
        WHERE $entity_name IN e.all_names
        RETURN 
            properties(e) AS entity,
            r.predicate AS predicate,
            properties(r) AS relationship_props,
            properties(other) AS related_entity,
            CASE WHEN startNode(r) = e THEN 'outgoing' ELSE 'incoming' END AS direction
        """
        result = tx.run(query, entity_name=entity_name)
        dict_list_rel = [
            dict(record) for record in result if check_not_incoming(dict(record))
        ]
        return [create_triplet_from_dict(dic) for dic in dict_list_rel]

    @staticmethod
    def _get_triplets_by_chapter_tx(tx, chapter_idx: int) -> List[InputTriplet]:
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
        filtered_result = [
            dict(record) for record in result if check_not_incoming(dict(record))
        ]
        return [create_triplet_from_dict(dict(record)) for record in filtered_result]
