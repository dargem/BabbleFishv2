"""Neo4j connection management for the knowledge graph"""

import os
from typing import Optional
from dotenv import load_dotenv
from neo4j import GraphDatabase, Driver

load_dotenv(override=True)


class Neo4jConnection:
    """Manages Neo4j database connection"""

    def __init__(self):
        """Initialize the Neo4j connection"""
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

    def get_driver(self) -> Driver:
        """Get the Neo4j driver instance"""
        return self.driver
