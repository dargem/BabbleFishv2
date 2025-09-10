"""Entity operations for the knowledge graph"""

from typing import List, Dict, Any, Optional
from neo4j import Driver
from src.models.node import Entity, EntityType
from .utils import reconstruct_entities


class EntityOperations:
    """Handles entity-related operations in the knowledge graph"""

    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver"""
        self.driver = driver

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
            entities_data = session.execute_read(
                self._get_entities_by_type_tx, entity_type
            )
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

    # Transaction methods

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
