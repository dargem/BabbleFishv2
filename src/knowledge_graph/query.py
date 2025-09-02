"""Query utilities for the knowledge graph"""

from typing import List, Dict, Any, Optional, Set
from .graph_manager import KnowledgeGraphManager
from .models import EntityType


class KnowledgeGraphQuery:
    """High-level query interface for the knowledge graph"""

    def __init__(self, graph_manager: KnowledgeGraphManager):
        self.graph_manager = graph_manager

    def find_entities_by_chapter(self, chapter_idx: int) -> List[Dict[str, Any]]:
        """
        Find all entities mentioned in a specific chapter

        Args:
            chapter_idx: Chapter index

        Returns:
            List of entities from the chapter
        """
        with self.graph_manager.driver.session() as session:
            return session.execute_read(self._find_entities_by_chapter_tx, chapter_idx)

    def find_connected_entities(
        self, entity_name: str, max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Find entities connected to a given entity within max_depth hops

        Args:
            entity_name: Name of the source entity
            max_depth: Maximum relationship depth to traverse

        Returns:
            List of connected entities with path information
        """
        with self.graph_manager.driver.session() as session:
            return session.execute_read(
                self._find_connected_entities_tx, entity_name, max_depth
            )

    def find_entity_mentions_across_chapters(
        self, entity_name: str
    ) -> List[Dict[str, Any]]:
        """
        Find all chapters where an entity is mentioned (through relationships)

        Args:
            entity_name: Name of the entity

        Returns:
            List of chapter information where entity appears
        """
        with self.graph_manager.driver.session() as session:
            return session.execute_read(self._find_entity_mentions_tx, entity_name)

    def find_entities_by_relationship(
        self, predicate: str, chapter_idx: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find all entities connected by a specific relationship type

        Args:
            predicate: The relationship predicate to search for
            chapter_idx: Optional chapter filter

        Returns:
            List of entity pairs connected by the relationship
        """
        with self.graph_manager.driver.session() as session:
            return session.execute_read(
                self._find_entities_by_relationship_tx, predicate, chapter_idx
            )

    def get_character_interactions(
        self, chapter_idx: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get interactions between Person entities

        Args:
            chapter_idx: Optional chapter filter

        Returns:
            List of character interactions
        """
        with self.graph_manager.driver.session() as session:
            return session.execute_read(
                self._get_character_interactions_tx, chapter_idx
            )

    def find_similar_entities(
        self, entity_name: str, similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """
        Find entities with similar names (for potential merging)

        Args:
            entity_name: Name to find similar entities for
            similarity_threshold: Similarity threshold (0-1)

        Returns:
            List of potentially similar entities
        """
        with self.graph_manager.driver.session() as session:
            return session.execute_read(
                self._find_similar_entities_tx, entity_name, similarity_threshold
            )

    def get_temporal_relationships(self, temporal_type: str) -> List[Dict[str, Any]]:
        """
        Get relationships of a specific temporal type

        Args:
            temporal_type: "static", "dynamic", or "atemporal"

        Returns:
            List of relationships with the specified temporal type
        """
        with self.graph_manager.driver.session() as session:
            return session.execute_read(
                self._get_temporal_relationships_tx, temporal_type
            )

    def get_chapter_narrative_graph(self, chapter_idx: int) -> Dict[str, Any]:
        """
        Get a complete narrative graph for a chapter

        Args:
            chapter_idx: Chapter index

        Returns:
            Dictionary containing entities and relationships for the chapter
        """
        entities = self.find_entities_by_chapter(chapter_idx)
        triplets = self.graph_manager.get_triplets_by_chapter(chapter_idx)

        return {
            "chapter": chapter_idx,
            "entities": entities,
            "relationships": triplets,
            "entity_count": len(entities),
            "relationship_count": len(triplets),
        }

    # Transaction methods
    @staticmethod
    def _find_entities_by_chapter_tx(tx, chapter_idx: int) -> List[Dict[str, Any]]:
        """Transaction to find entities by chapter"""
        query = """
        MATCH (e:Entity)
        WHERE e.chapter_idx = $chapter_idx
        RETURN properties(e) AS entity
        UNION
        MATCH (e:Entity)-[r]-()
        WHERE r.chapter_idx = $chapter_idx
        RETURN DISTINCT properties(e) AS entity
        """
        result = tx.run(query, chapter_idx=chapter_idx)
        return [record["entity"] for record in result]

    @staticmethod
    def _find_connected_entities_tx(
        tx, entity_name: str, max_depth: int
    ) -> List[Dict[str, Any]]:
        """Transaction to find connected entities"""
        query = """
        MATCH (start:Entity)
        WHERE $entity_name IN start.names
        MATCH path = (start)-[*1..$max_depth]-(connected:Entity)
        RETURN 
            properties(connected) AS entity,
            length(path) AS distance,
            [rel IN relationships(path) | {predicate: rel.predicate, chapter: rel.chapter_idx}] AS path_info
        """
        result = tx.run(query, entity_name=entity_name, max_depth=max_depth)
        return [dict(record) for record in result]

    @staticmethod
    def _find_entity_mentions_tx(tx, entity_name: str) -> List[Dict[str, Any]]:
        """Transaction to find entity mentions across chapters"""
        query = """
        MATCH (e:Entity)-[r]-()
        WHERE $entity_name IN e.names AND r.chapter_idx IS NOT NULL
        RETURN DISTINCT r.chapter_idx AS chapter, COUNT(r) AS mention_count
        ORDER BY chapter
        """
        result = tx.run(query, entity_name=entity_name)
        return [dict(record) for record in result]

    @staticmethod
    def _find_entities_by_relationship_tx(
        tx, predicate: str, chapter_idx: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Transaction to find entities by relationship"""
        base_query = """
        MATCH (subject:Entity)-[r:RELATES]->(object:Entity)
        WHERE r.predicate = $predicate
        """

        if chapter_idx is not None:
            base_query += " AND r.chapter_idx = $chapter_idx"

        base_query += """
        RETURN 
            properties(subject) AS subject_entity,
            properties(object) AS object_entity,
            properties(r) AS relationship
        """

        params = {"predicate": predicate}
        if chapter_idx is not None:
            params["chapter_idx"] = chapter_idx

        result = tx.run(base_query, **params)
        return [dict(record) for record in result]

    @staticmethod
    def _get_character_interactions_tx(
        tx, chapter_idx: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Transaction to get character interactions"""
        base_query = """
        MATCH (p1:Entity)-[r:RELATES]-(p2:Entity)
        WHERE p1.entity_type = 'Person' AND p2.entity_type = 'Person'
        """

        if chapter_idx is not None:
            base_query += " AND r.chapter_idx = $chapter_idx"

        base_query += """
        RETURN 
            properties(p1) AS person1,
            properties(p2) AS person2,
            properties(r) AS interaction
        """

        params = {}
        if chapter_idx is not None:
            params["chapter_idx"] = chapter_idx

        result = tx.run(base_query, **params)
        return [dict(record) for record in result]

    @staticmethod
    def _find_similar_entities_tx(
        tx, entity_name: str, similarity_threshold: float
    ) -> List[Dict[str, Any]]:
        """Transaction to find similar entities (simple name-based similarity)"""
        query = """
        MATCH (e:Entity)
        WHERE ANY(name IN e.names WHERE 
            apoc.text.distance(toLower($entity_name), toLower(name)) >= $threshold)
        AND NOT $entity_name IN e.names
        RETURN 
            properties(e) AS entity,
            [name IN e.names WHERE 
                apoc.text.distance(toLower($entity_name), toLower(name)) >= $threshold][0] AS similar_name
        """
        result = tx.run(
            query, entity_name=entity_name.lower(), threshold=similarity_threshold
        )
        return [dict(record) for record in result]

    @staticmethod
    def _get_temporal_relationships_tx(tx, temporal_type: str) -> List[Dict[str, Any]]:
        """Transaction to get temporal relationships"""
        query = """
        MATCH (subject:Entity)-[r:RELATES]->(object:Entity)
        WHERE r.temporal_type = $temporal_type
        RETURN 
            properties(subject) AS subject_entity,
            properties(object) AS object_entity,
            properties(r) AS relationship
        ORDER BY r.chapter_idx
        """
        result = tx.run(query, temporal_type=temporal_type)
        return [dict(record) for record in result]
