"""Entity operations for the knowledge graph"""

from typing import List, Dict, Any, Optional
from neo4j import Driver
from src.core import Entity, EntityType
from .utils import reconstruct_entities


class EntityOperations:
    """Handles entity-related operations in the knowledge graph"""

    def __init__(self, driver: Driver):
        """Initialize with Neo4j driver"""
        self.driver = driver

    def update_entities(self, entities: List[Entity]) -> int:
        """
        Updates multiple entities into the knowledge graph.

        For each entity:
        - If it matches existing entities by strong names, merge them
        - If it's a merge of multiple entities, combine their edges
        - If it doesn't exist, create a new node

        Args:
            entities: List of entities to update

        Returns:
            Number of entities processed
        """
        with self.driver.session() as session:
            return session.execute_write(self._update_entities_tx, entities)

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
        record = result.single
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
    def _update_entities_tx(tx, entities: List[Entity]) -> int:
        """Transaction to update multiple entities with merge logic"""
        entities_processed = 0

        for entity in entities:
            if not entity.strong_names:
                # No strong names - create as new entity
                EntityOperations._create_new_entity(tx, entity)
                entities_processed += 1
                continue

            # Find existing entities that share strong names
            existing_entities = EntityOperations._find_matching_entities(
                tx, entity.strong_names
            )

            if not existing_entities:
                # No matches found - create new entity
                EntityOperations._create_new_entity(tx, entity)
                entities_processed += 1
            else:
                # Merge with existing entities
                EntityOperations._merge_entities(tx, entity, existing_entities)
                entities_processed += 1

        return entities_processed

    @staticmethod
    def _find_matching_entities(tx, strong_names: List[str]) -> List[Dict[str, Any]]:
        """Find existing entities that share any strong names"""
        if not strong_names:
            return []

        query = """
        MATCH (e:Entity)
        WHERE ANY(existing_name IN e.strong_names 
                  WHERE existing_name IN $strong_names)
        RETURN e, properties(e) AS props
        """
        return list(tx.run(query, strong_names=strong_names))

    @staticmethod
    def _create_new_entity(tx, entity: Entity) -> None:
        """Create a new entity node"""
        query = """
        CREATE (e:Entity)
        SET e = $props
        RETURN e
        """
        tx.run(query, props=entity.to_neo4j_props())

    @staticmethod
    def _merge_entities(
        tx, new_entity: Entity, existing_entities: List[Dict[str, Any]]
    ) -> None:
        """Merge new entity with existing entities, preserving relationships"""
        # Use element IDs instead of Node objects
        existing_node_ids = [record["e"].element_id for record in existing_entities]

        # Collect all relationships from existing entities
        relationships = EntityOperations._collect_relationships(tx, existing_node_ids)

        # Delete old entities
        EntityOperations._delete_entities(tx, existing_node_ids)

        # Create new merged entity
        new_node = EntityOperations._create_merged_entity(tx, new_entity)

        # Recreate relationships with new entity
        EntityOperations._recreate_relationships(tx, new_node, relationships)

    @staticmethod
    def _collect_relationships(tx, nodes: List[Any]) -> List[Dict[str, Any]]:
        """Collect all relationships from given nodes"""
        query = """
        MATCH (e:Entity)-[r:RELATES]-(other)
        WHERE elementId(e) IN $node_ids
        RETURN e, r, other, r.predicate AS rel_type, 
               startNode(r) = e AS is_outgoing,
               properties(r) AS rel_props
        """
        return list(tx.run(query, node_ids=nodes))

    @staticmethod
    def _delete_entities(tx, nodes: List[Any]) -> None:
        """Delete entities and their relationships"""
        query = """
        MATCH (e:Entity)
        WHERE elementId(e) IN $node_ids
        DETACH DELETE e
        """
        tx.run(query, node_ids=nodes)

    @staticmethod
    def _create_merged_entity(tx, entity: Entity) -> Any:
        """Create the new merged entity"""
        query = """
        CREATE (new_e:Entity)
        SET new_e = $props
        RETURN new_e
        """
        result = tx.run(query, props=entity.to_neo4j_props())
        return result.single()["new_e"]

    @staticmethod
    def _recreate_relationships(
        tx, new_entity: Any, relationships: List[Dict[str, Any]]
    ) -> None:
        """Recreate relationships with the new entity, avoiding duplicates"""
        unique_relationships = EntityOperations._deduplicate_relationships(
            relationships
        )

        for rel_info in unique_relationships.values():
            EntityOperations._create_relationship(tx, new_entity, rel_info)

    @staticmethod
    def _deduplicate_relationships(
        relationships: List[Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """Remove duplicate relationships"""
        unique_relationships = {}

        for rel_record in relationships:
            other_node = rel_record["other"]
            rel_type = rel_record["rel_type"]
            is_outgoing = rel_record["is_outgoing"]
            rel_props = rel_record["rel_props"]

            # Create unique key for relationship
            direction = "outgoing" if is_outgoing else "incoming"
            rel_key = (other_node.element_id, rel_type, direction)

            if rel_key not in unique_relationships:
                unique_relationships[rel_key] = {
                    "other": other_node,
                    "type": rel_type,
                    "outgoing": is_outgoing,
                    "properties": rel_props,
                }

        return unique_relationships

    @staticmethod
    def _create_relationship(tx, new_entity: Any, rel_info: Dict[str, Any]) -> None:
        """Create a single relationship"""
        rel_type = rel_info["type"]

        if rel_info["outgoing"]:
            # Use dynamic query construction for relationship type
            query = f"""
            MATCH (new_e:Entity), (other)
            WHERE elementId(new_e) = $new_id AND elementId(other) = $other_id
            CREATE (new_e)-[r:`{rel_type}`]->(other)
            SET r = $rel_props
            RETURN r
            """
        else:
            query = f"""
            MATCH (new_e:Entity), (other)
            WHERE elementId(new_e) = $new_id AND elementId(other) = $other_id
            CREATE (other)-[r:`{rel_type}`]->(new_e)
            SET r = $rel_props
            RETURN r
            """

        tx.run(
            query,
            new_id=new_entity.element_id,
            other_id=rel_info["other"].element_id,
            rel_props=rel_info["properties"],
        )
