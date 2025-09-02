"""
Responsible for managing additions into the database, both for entities and relationships
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from ..models import Entity, EntityType
from typing import List

load_dotenv(override=True)

neo4j_uri = os.getenv("NEO4J_URI")
neo4j_user = "neo4j"
neo4j_password = os.getenv("NEO4J_PASS")

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))


def _execute_write(query):
    with driver.session() as session:
        session.execute_write(reset_database)


def _execute_read(query):
    with driver.session() as session:
        return session.execute_read(reset_database)


# some sample query/writes
def add_entities(entities: List[Entity]):
    query = ""


def add_entity(tx, entity: Entity):
    tx.run(
        """
        CREATE (e:Entity {
            names: $names,
            translation: $translation,
            description: $description,
            type: $type,
            chapter_idx: $chapter_idx
        })
        """,
        names=entity.names,
        translation=entity.translation,
        description=entity.description,
        type=entity.type.name,
        chapter_idx=entity.chapter_idx,
    )


def get_entities(tx):
    result = tx.run("MATCH (e:Entity) RETURN e.names AS names")
    return [record["names"] for record in result]


def reset_database(tx):
    tx.run("MATCH (n) DETACH DELETE n")


# Using sessions to execute queries
with driver.session() as session:
    session.execute_write(reset_database)
    e = Entity(
        names=["Alice", "Alicia"],
        translation="Αλίκη",
        description="A curious adventurer",
        type_=EntityType.PERSON,
        chapter_idx=1,
    )
    session.execute_write(add_entity, e)
    print(session.execute_read(get_entities))


driver.close()
