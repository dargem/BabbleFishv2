"""Knowledge graph manager for Neo4j operations"""

from typing import List, Dict, Any, Optional
from src.models.node import Entity
from src.models.edge import Triplet, EntityType
from .connection import Neo4jConnection
from .entity_operations import EntityOperations
from .triplet_operations import TripletOperations
from .database_operations import DatabaseOperations


class KnowledgeGraphManager:
    """Facade for knowledge graph operations with Neo4j"""

    def __init__(self):
        """Initialize the knowledge graph manager"""
        self._connection = Neo4jConnection()
        self.driver = self._connection.get_driver()

        # Initialize operation handlers
        self._entity_ops = EntityOperations(self.driver)
        self._triplet_ops = TripletOperations(self.driver)
        self._db_ops = DatabaseOperations(self.driver)

    def close(self):
        """Close the Neo4j driver connection"""
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # Entity operations - delegate to EntityOperations

    def add_entities(self, entities: List[Entity]) -> int:
        """
        Add multiple entities to the knowledge graph

        Args:
            entities: List of entities to add

        Returns:
            Number of entities created
        """
        return self._entity_ops.add_entities(entities)

    def find_entity_by_name(self, name: str) -> Optional[Entity]:
        """
        Find an entity by any of its names

        Args:
            name: Name to search for

        Returns:
            Entity object if found, None otherwise
        """
        return self._entity_ops.find_entity_by_name(name)

    def get_entities_by_type(self, entity_type: EntityType) -> List[Entity]:
        """
        Get all entities of a specific type

        Args:
            entity_type: Type of entities to retrieve

        Returns:
            List of Entity objects
        """
        return self._entity_ops.get_entities_by_type(entity_type)

    def get_all_entities(self) -> List[Entity]:
        """
        Get all entities in the knowledge graph

        Returns:
            List of all Entity objects
        """
        return self._entity_ops.get_all_entities()

    # Triplet operations - delegate to TripletOperations

    def add_triplets(self, triplets: List[Triplet]) -> int:
        """
        Add multiple triplets to the knowledge graph

        Args:
            triplets: List of triplets to add

        Returns:
            Number of relationships created
        """
        return self._triplet_ops.add_triplets(triplets)

    def get_entity_relationships(self, entity_name: str) -> List[Dict[str, Any]]:
        """
        Get all relationships for an entity

        Args:
            entity_name: Name of the entity

        Returns:
            List of relationships with their properties
        """
        return self._triplet_ops.get_entity_relationships(entity_name)

    def get_triplets_by_chapter(self, chapter_idx: int) -> List[Dict[str, Any]]:
        """
        Get all triplets from a specific chapter

        Args:
            chapter_idx: Chapter index

        Returns:
            List of triplets from the chapter
        """
        return self._triplet_ops.get_triplets_by_chapter(chapter_idx)

    # Utility operations - delegate to DatabaseOperations
    def reset_database(self) -> int:
        """
        Delete all nodes and relationships in the database

        Returns:
            Number of nodes deleted
        """
        return self._db_ops.reset_database()

    def get_stats(self) -> Dict[str, int]:
        """
        Get basic statistics about the knowledge graph

        Returns:
            Dictionary with entity and relationship counts
        """
        return self._db_ops.get_stats()
