"""Knowledge graph manager for Neo4j operations"""

import os
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv
from neo4j import GraphDatabase, Driver, Session
from src.models.graph_data import Entity, Triplet, EntityType, TripletMetadata
from .utils import reconstruct_entities

load_dotenv(override=True)


class KnowledgeGraphManager:
    """Manager for knowledge graph operations with Neo4j"""

    def __init__(self):
        """Initialize the knowledge graph manager"""
        neo4j_uri = os.getenv("NEO4J_URI")
        neo4j_user = "neo4j"
        neo4j_password = os.getenv("NEO4J_PASS")

        if not all([neo4j_uri, neo4j_password]):
            raise ValueError("Neo4j credentials not found in environment variables")

        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    def close(self):
        """Close the Neo4j driver connection"""
        if self.driver:
            self.driver.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # Entity operations
    def add_entity(self, entity: Entity) -> bool:
        """
        Add a single entity to the knowledge graph

        Args:
            entity: Entity to add

        Returns:
            True if entity was created, False if it already existed
        """
        with self.driver.session() as session:
            return session.execute_write(self._add_entity_tx, entity)

    def add_entities(self, entities: List[Entity]) -> int:
        """
        Add multiple entities to the knowledge graph

        Args:
            entities: List of entities to add

        Returns:
            Number of entities created
        """
        with self.driver.session() as session:
            return session.execute_write(self._add_entities_tx, entities)

    def find_entity_by_name(self, name: str) -> Optional[Entity]:
        """
        Find an entity by any of its names

        Args:
            name: Name to search for

        Returns:
            Entity object if found, None otherwise
        """
        with self.driver.session() as session:
            entity_data = session.execute_read(self._find_entity_by_name_tx, name)
            if entity_data:
                return reconstruct_entities([entity_data])[0]
            return None

    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """
        Get all entities of a specific type

        Args:
            entity_type: Type of entities to retrieve

        Returns:
            List of Entity objects
        """
        with self.driver.session() as session:
            entities_data = session.execute_read(self._get_entities_by_type_tx, entity_type)
            return reconstruct_entities(entities_data)

    def get_all_entities(self) -> List[Entity]:
        """
        Get all entities in the knowledge graph

        Returns:
            List of all Entity objects
        """
        with self.driver.session() as session:
            entities_data = session.execute_read(self._get_all_entities_tx)
            return reconstruct_entities(entities_data)

    # Triplet operations
    def add_triplet(self, triplet: Triplet) -> bool:
        """
        Add a triplet (relationship) to the knowledge graph

        Args:
            triplet: Triplet to add

        Returns:
            True if relationship was created, False if entities not found
        """
        with self.driver.session() as session:
            return session.execute_write(self._add_triplet_tx, triplet)

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

    # Utility operations
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
    def _add_entity_tx(tx, entity: Entity) -> bool:
        """Transaction to add a single entity"""
        query = """
        MERGE (e:Entity {all_names: $all_names})
        ON CREATE SET e += $props
        RETURN COUNT(e) > 0 AS created
        """
        props = entity.to_neo4j_props()
        result = tx.run(query, all_names=entity.all_names, props=props)
        return result.single()["created"]

    @staticmethod
    def _add_entities_tx(tx, entities: List[Entity]) -> int:
        """Transaction to add multiple entities"""
        query = """
        UNWIND $entities AS entity_data
        MERGE (e:Entity {all_names: entity_data.all_names})
        ON CREATE SET e += entity_data.props
        RETURN COUNT(e) AS created
        """
        entity_data = [
            {"all_names": entity.all_names, "props": entity.to_neo4j_props()}
            for entity in entities
        ]
        result = tx.run(query, entities=entity_data)
        return result.single()["created"]

    @staticmethod
    def _find_entity_by_name_tx(tx, name: str) -> Optional[Dict[str, Any]]:
        """Transaction to find entity by name"""
        query = """
        MATCH (e:Entity)
        WHERE $name IN e.all_names
        RETURN properties(e) AS entity
        LIMIT 1
        """
        result = tx.run(query, name=name)
        record = result.single()
        return record["entity"] if record else None

    @staticmethod
    def _get_entities_by_type_tx(tx, entity_type: EntityType) -> List[Dict[str, Any]]:
        """Transaction to get entities by type"""
        query = """
        MATCH (e:Entity)
        WHERE e.entity_type = $entity_type
        RETURN properties(e) AS entity
        """
        result = tx.run(query, entity_type=entity_type.value)
        return [record["entity"] for record in result]

    @staticmethod
    def _get_all_entities_tx(tx) -> List[Dict[str, Any]]:
        """Transaction to get all entities"""
        query = "MATCH (e:Entity) RETURN properties(e) AS entity"
        result = tx.run(query)
        return [record["entity"] for record in result]

    @staticmethod
    def _add_triplet_tx(tx, triplet: Triplet) -> bool:
        """Transaction to add a triplet"""
        query = """
        MATCH (subject:Entity), (object:Entity)
        WHERE $subject_name IN subject.all_names AND $object_name IN object.all_names
        MERGE (subject)-[r:RELATES {predicate: $predicate}]->(object)
        ON CREATE SET r += $metadata
        RETURN COUNT(r) > 0 AS created
        """
        result = tx.run(
            query,
            subject_name=triplet.subject_name,
            object_name=triplet.object_name,
            predicate=triplet.predicate,
            metadata=triplet.metadata.to_neo4j_props(),
        )
        return result.single()["created"]

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
